from napalm_sros import NokiaSROSDriver
from napalm.base import models as napalm_models

from lxml import etree
from ncclient.xml_ import to_ele, to_xml

from ..base import SCBaseNetconfDriver, sc_models
from .nc_filters import GET_INVENTORY


class SCNokiaSROSDriver(NokiaSROSDriver, SCBaseNetconfDriver):
    netmiko_host_type = "alcatel_sros"

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        if format != "text":
            return super().get_config(
                retrieve=retrieve, full=full, sanitized=sanitized, format=format
            )

        config = {"startup": "", "running": "", "candidate": ""}

        with self.ssh_conn() as ssh_device:
            config["running"] = ssh_device.send_command("admin show configuration flat")
            config["running"] += ssh_device.send_command(
                "admin show configuration bof flat"
            )

        return config

    # def get_inventory(self) -> list[sc_models.InventoryDict]:

    #     result = to_ele(
    #             self.conn.get(filter=GET_INVENTORY["_"], with_defaults="report-all").data_xml
    #     )
    #     print(etree.tostring(result, pretty_print=True, encoding="unicode"))
