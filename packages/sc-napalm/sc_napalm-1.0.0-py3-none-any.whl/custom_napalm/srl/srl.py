from napalm_srl import NokiaSRLDriver
from napalm_srl.srl import SRLAPI
from napalm.base import models as napalm_models
from ..base import SCBaseNetconfDriver

from ipaddress import IPv6Address

from pprint import pprint


class SCSLRAPI(SRLAPI):
    """
    This override fixes an issue with IPv6 addresses embedded in URLs when talking
    over GRPCs. Not sure if it's moot with the various TLS
    """

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        super().__init__(hostname, username, password, timeout, optional_args)

        try:
            IPv6Address(hostname)
            self.target = f"[{hostname}]:{self.gnmi_port}"
        except ValueError:
            pass


class SCNokiaSRLDriver(NokiaSRLDriver, SCBaseNetconfDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing insecure connection for testing purposes
        """
        optional_args = optional_args if optional_args else {}
        optional_args["insecure"] = True
        optional_args["skip_verify"] = True

        optional_args["encoding"] = "JSON_IETF"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

        self.device = SCSLRAPI(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        """
        pulling running config via ssh sow we can have it in 'display set' format.
        """
        if format != "text":
            return super().get_config(
                retrieve=retrieve, full=full, sanitized=sanitized, format=format
            )

        config = {"startup": "", "running": "", "candidate": ""}

        with self.ssh_conn() as ssh_device:
            if retrieve in ["all", "running"]:
                config["running"] = ssh_device.send_command("info from running flat")
            if retrieve in ["all", "startup"]:
                config["startup"] = ssh_device.send_command("info from startup flat")
            if retrieve in ["all", "candidate"]:
                config["candidate"] = ssh_device.send_command(
                    "info from candidate flat"
                )

        return config

    def get_optics(self):
        path = {"/interface"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        interfaces = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        channel_data = {}

        for i in interfaces:
            if not self._getObj(i, *["transceiver", "channel"], default=False):
                continue

            name = self._getObj(i, *["name"])
            channel = self._getObj(i, *["transceiver", "channel"], default={})[0]
            channel_data.update(
                {
                    name: {
                        "physical_channels": {
                            "channel": [
                                {
                                    "index": self._getObj(
                                        channel, *["index"], default=-1
                                    ),
                                    "state": {
                                        "input_power": {
                                            "instant": self._getObj(
                                                channel,
                                                *["input-power", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                        "output_power": {
                                            "instant": self._getObj(
                                                channel,
                                                *["output-power", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                        "laser_bias_current": {
                                            "instant": self._getObj(
                                                channel,
                                                *["laser-bias-current", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                    },
                                }
                            ]
                        }
                    }
                }
            )

        return channel_data

    def get_inventory(self):
        path = {"/interface/transceiver"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        transceivers = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        result = []
        for t_if in transceivers:
            trans = t_if["transceiver"]

            if "serial-number" not in trans:
                continue

            result.append(
                {
                    "type": "optic",
                    "subtype": trans["ethernet-pmd"],
                    "name": t_if["name"],
                    "part_number": trans["vendor-part-number"],
                    "serial_number": trans["serial-number"],
                }
            )

        return result
