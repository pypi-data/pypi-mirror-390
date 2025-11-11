from typing import List
import logging

from napalm.nxos_ssh import NXOSSSHDriver
from napalm.base.helpers import textfsm_extractor

from ..base import SCBaseDriver
from ..models import (
    InventoryDict,
)

logger = logging.getLogger(__name__)


class SCNXOS(NXOSSSHDriver, SCBaseDriver):
    """
    NXOS Parser
    """

    # for nexus we're going to map the 'description' provided by
    # show inventory to the type
    INVENTORY_TO_TYPE = {
        # note we're using the fact that this dict gets evaluated
        # sequentially to catch the linecards, whose descriptions are varied
        # but all end in 'Module'
        r"Fabric Module": "fabric_module",
        r"Fabric card": "fabric_module",  # N7K fabric modules in umd
        r"Fabric Extender": None,  # FEXes in Dearborn
        r"N2K-C2": "stack_member",  # FEXes in Dearborn
        r"Eth\s?Mod": None,  # chassis for fixed config Nexus
        r"Supervisor Module": "re",
        r"Fan Module": "fan",
        r"Module": "linecard",
        r"System Controller": None,
        r"Chassis": None,
        r"Power Supply": "psu",
    }

    I_ABBRS = {
        "Lo": "loopback",
        "Po": "port-channel",
        "Eth": "Ethernet",
    }

    def get_inventory(self) -> List[InventoryDict]:
        """
        Parses "show inventory" and "show interface transciever"
        """

        raw_inventory = self._send_command("show inventory")
        inventory = textfsm_extractor(self, "sh_inventory", raw_inventory)

        output = []
        for entry in inventory:
            inventory_type = self._get_inventory_type(entry["desc"])
            if not inventory_type:
                continue

            output.append(
                {
                    "type": inventory_type,
                    "name": entry["name"],
                    "part_number": entry["pid"],
                    "serial_number": entry["sn"],
                }
            )

        raw_trans = self._send_command("show interface transceiver")
        trans = textfsm_extractor(self, "sh_int_transceiver", raw_trans)
        for entry in trans:
            if "AOC" in entry["type"]:
                db_type = "aoc"
            elif "DAC" in entry["type"]:
                db_type = "dac"
            else:
                db_type = "optic"

            output.append(
                {
                    "type": db_type,
                    "subtype": entry["type"],
                    "name": entry["interface"],
                    "part_number": entry["pn"],
                    "serial_number": entry["sn"],
                }
            )

        return output
