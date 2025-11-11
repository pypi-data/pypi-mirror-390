from typing import Dict, List

from ncclient import manager
from ncclient.xml_ import to_ele
from lxml import etree

from napalm.base import NetworkDriver
from napalm.base.exceptions import ConnectionException
from napalm.base import models as napalm_models


import logging

from ..base import SCBaseNetconfDriver
from .. import models as sc_models
from . import constants as C
from .constants import NS

logger = logging.getLogger(__name__)


class SCNOSDriver(NetworkDriver, SCBaseNetconfDriver):
    """
    Drivenets class is heavily based on Napalm IOSXR, which is
    also a netconf/yang device.
    """

    netmiko_host_type = "linux"

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.pending_changes = False
        self.replace = False
        self.locked = False
        self.optional_args = optional_args if optional_args else {}
        self.port = self.optional_args.pop("port", 830)
        self.key_file = self.optional_args.pop("key_file", None)
        if "ssh_config_file" in self.optional_args:
            #    self.optional_args["ssh_config"] = self.optional_args["ssh_config_file"]
            del self.optional_args["ssh_config_file"]

        self.optional_args["hostkey_verify"] = False
        self.device = None
        self.NS = NS

    def open(self):
        """Open the connection with the device."""
        try:
            self.device = manager.connect(
                host=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=self.key_file,
                timeout=self.timeout,
                **self.optional_args,
            )

        except Exception as conn_err:
            logger.error(conn_err.args[0])
            raise ConnectionException(conn_err.args[0])

    def close(self):
        """Close the connection."""
        logger.debug("Closed connection with device %s" % (self.hostname))
        self.device.close_session()

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        """
        Get config adapted from iosxr_netconf driver. Note that there doesn't appear to
        be a way to get a non-xml version of the config via netconf, so we're doing
        in a separate SSH CLI session.
        """

        if sanitized:
            raise NotImplementedError("Sanitized nos config not supported")
        if format not in ["text", "xml"]:
            raise NotImplementedError("Only XML and text config formats supported")

        config = {"startup": "", "running": "", "candidate": ""}

        # for text format we're going to SSH into the device and do 'show config'
        # in this scenario 'candidate' isn't really relevant.
        if format == "text":
            with self.ssh_conn() as ssh_device:
                config["running"] = ssh_device.send_command("show config")

        # otherwise we're just doing netconf 'get-config'
        else:
            if retrieve.lower() in ["running", "all"]:
                config["running"] = str(self.device.get_config(source="running").xml)
            if retrieve.lower() in ["candidate", "all"]:
                config["candidate"] = str(
                    self.device.get_config(source="candidate").xml
                )

            for datastore in config:
                if not config[datastore]:
                    continue

                config[datastore] = etree.tostring(
                    etree.fromstring(config[datastore][0]),
                    pretty_print=True,
                    encoding="unicode",
                )

        return config

    def get_facts(self) -> napalm_models.FactsDict:
        """napalm get_facts"""
        rpc_reply = self.device.dispatch(to_ele(C.FACTS_RPC_REQ)).xml
        facts_xml = etree.fromstring(rpc_reply)

        return {
            "vendor": "Drivenets",
            "os_version": self._text(facts_xml, "//dn-sys:system-version", default=""),
            "hostname": self._text(facts_xml, "//dn-sys:name", default=""),
            "uptime": self._text(facts_xml, "//dn-sys:system-uptime", default=-1.0),
            "serial_number": self._text(
                facts_xml, "//dn-platform:serial-number", default=""
            ),
            "fqdn": self._text(facts_xml, "//dn-sys-dns:domain-name", default=""),
            "model": self._text(facts_xml, "//dn-sys:system-type", default=""),
            "interface_list": [i.text for i in self._xpath(facts_xml, "//dn-if:name")],
        }

    def get_optics(self) -> Dict[str, napalm_models.OpticsDict]:
        """napalm get_optics"""
        rpc_reply = self.device.dispatch(to_ele(C.OPTICS_RPC_REQ)).xml
        optics_xml = etree.fromstring(rpc_reply)

        # print(etree.tostring(optics_xml, pretty_print=True, encoding="unicode"))

        output = {}
        for i in self._xpath(optics_xml, "//dn-if:interface"):
            if not self._text(i, ".//dn-trans:transceiver-voltage"):
                continue
            i_name = self._text(i, "dn-if:name")
            output[i_name] = {"physical_channels": {"channels": {}}}

            i_channels = output[i_name]["physical_channels"]["channels"]
            for c in self._xpath(i, ".//dn-trans:channel"):
                if self._text(c, ".//dn-trans:receive-power"):
                    i_channels[self._text(c, ".//dn-trans:lane")] = {
                        "input_power": self._text(c, ".//dn-trans:receive-power"),
                        "output_power": self._text(c, ".//dn-trans:transmit-power"),
                        "laser_bias_current": self._text(
                            c, ".//dn-trans:laser-bias-current"
                        ),
                    }

        return output

    def get_lldp_neighbors(self) -> Dict[str, List[napalm_models.LLDPNeighborDict]]:
        """napalm get lldp neighbors"""
        rpc_reply = self.device.dispatch(to_ele(C.LLDP_NEIGH_RPC_REQ)).xml
        lldp_xml = etree.fromstring(rpc_reply)

        # print(etree.tostring(lldp_xml, pretty_print=True, encoding="unicode"))

        output = {}
        for i in self._xpath(lldp_xml, "//dn-lldp:interface"):
            if not self._xpath(i, ".//dn-lldp:system-name"):
                continue
            i_name = self._text(i, ".//dn-lldp:name")
            output[i_name] = []

            for n in self._xpath(i, ".//dn-lldp:neighbor"):
                output[i_name].append(
                    {
                        "hostname": self._text(n, ".//dn-lldp:system-name"),
                        "port": self._text(n, ".//dn-lldp:port-id"),
                    }
                )

        return output

    def get_inventory(self) -> List[sc_models.InventoryDict]:
        """
        sc-napalm get inventory
        """
        rpc_reply = self.device.dispatch(to_ele(C.INVENTORY_RPC_REQ)).xml
        inv_xml = etree.fromstring(rpc_reply)
        # print(etree.tostring(inv_xml, pretty_print=True, encoding="unicode"))

        output = []
        for i in self._xpath(inv_xml, "//dn-if:interface"):
            if not self._xpath(i, ".//dn-trans:ethernet-pmd"):
                continue

            i_name = self._text(i, "//dn-if:name")
            output.append(
                {
                    "type": "optic",
                    "subtype": self._get_optic_subtype(i),
                    "name": i_name,
                    "part_number": self._text(i, ".//dn-trans:vendor-part").strip(),
                    "serial_number": self._text(i, ".//dn-trans:serial-no").strip(),
                }
            )

        return output

    def _get_optic_subtype(self, i):
        """
        Optic subtypes are a bit tricky and sometimes have to be
        inferred
        """
        # the ethernet-pmd attribute gives us an official
        # 'transport type' which matches the data we want here
        eth_pmd = self._text(i, ".//dn-trans:ethernet-pmd")
        eth_pmd = eth_pmd.replace("dn-transport-types:", "")

        # terrible assumptions - right now on the one nos switch I only
        # see 'undefined' for 400G and 100G, wavelengths are all "1311"
        if eth_pmd == "ETH_UNDEFINED":
            speed = int(self._text(i, ".//dn-if:interface-speed")) / 1000
            if self._text(i, ".//dn-trans:wavelength") == "1311":
                return f"ETH_{int(speed)}GBASE-LR4"

            raise ValueError(
                f"ETH_UNDEFINED {i[0].text} speed {speed} WAVELENGTH {self._text(i, './/dn-trans:wavelength')}"
            )

        return eth_pmd
