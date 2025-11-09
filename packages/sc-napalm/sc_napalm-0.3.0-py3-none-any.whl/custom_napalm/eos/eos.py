from typing import List
from napalm.eos import EOSDriver
from ..base import SCBaseDriver
from ..models import InventoryDict


class SCEOSDriver(EOSDriver, SCBaseDriver):
    ("fabric_module",)
    ("fan",)
    ("linecard",)
    ("optic",)
    ("psu",)
    ("re",)
    ("stack_cable",)
    ("stack_member",)
    ("uplink_module",)
    ("aoc",)
    ("dac",)

    INVENTORY_TO_TYPE = {
        r"Fabric": "fabric_module",
        r"Linecard": "linecard",
        r"Supervisor": "re",
    }

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing ssh transport since we don't enable the web interface
        """
        optional_args = optional_args if optional_args else {}
        optional_args["transport"] = "ssh"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

    def get_inventory(self) -> List[InventoryDict]:
        inventory = self._run_commands(["show inventory"], encoding="json")

        results = []

        ### optics
        for slot, optic in inventory[0]["xcvrSlots"].items():
            if optic.get("modelName"):
                results.append(
                    {
                        "type": "optic",
                        "subtype": optic["modelName"],
                        "name": f"Ethernet{slot}",
                        "part_number": optic["modelName"],
                        "serial_number": optic["serialNum"],
                    },
                )

        ### line cards
        for slot, card in inventory[0]["cardSlots"].items():
            if card.get("serialNum"):
                results.append(
                    {
                        "type": self._get_inventory_type(slot),
                        "subtype": card["modelName"],
                        "name": f"Ethernet{slot}",
                        "part_number": card["modelName"],
                        "serial_number": card["serialNum"],
                    },
                )

        ### PSUs
        for slot, psu in inventory[0]["powerSupplySlots"].items():
            if psu.get("serialNum"):
                results.append(
                    {
                        "type": "psu",
                        "subtype": None,
                        "name": f"PSU {slot}",
                        "part_number": psu["name"],
                        "serial_number": psu["serialNum"],
                    },
                )

        ### FANs
        for slot, fan in inventory[0]["fanTraySlots"].items():
            if fan.get("serialNum"):
                results.append(
                    {
                        "type": "fan",
                        "subtype": None,
                        "name": f"FAN {slot}",
                        "part_number": fan["name"],
                        "serial_number": fan["serialNum"],
                    },
                )
        return results
