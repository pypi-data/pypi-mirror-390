from typing import List
import logging

from lxml import etree

from napalm.iosxr_netconf import IOSXRNETCONFDriver
from ncclient.xml_ import to_ele

from ..base import SCBaseNetconfDriver
from ..models import InventoryDict

from .constants import INV_RPC_REQ

logger = logging.getLogger(__name__)


class SCIOSXR(IOSXRNETCONFDriver, SCBaseNetconfDriver):
    """
    IOSXR Class
    """

    INVENTORY_TO_TYPE = {
        r"PM\d+$": "psu",
        r"FT\d+$": "fan",
        r"FC\d+$": "fabric_module",
        r"RP\d$": "re",
        r"SC\d": None,  # don't care about system controller
        r"Rack 0": None,  # this is the chassis, don't care about it
        r"^(FourHundred|Hundred|Forty)GigE": "optic",
        r"\d/\d": "linecard",
    }

    def get_inventory(self) -> List[InventoryDict]:
        """
        Gets inventory data
        """
        rpc_reply = self.device.dispatch(to_ele(INV_RPC_REQ)).xml
        xml_result = etree.fromstring(rpc_reply)

        output = []
        for item in self._xpath(xml_result, "//inv:inv-basic-bag"):
            name = self._text(item, "inv:name")
            item_type = self._get_inventory_type(name)
            if item_type:
                output.append(
                    {
                        "type": item_type,
                        "name": name,
                        "part_number": self._text(item, "inv:model-name"),
                        "serial_number": self._text(item, "inv:serial-number"),
                        "parent": None,
                    }
                )

        return output
