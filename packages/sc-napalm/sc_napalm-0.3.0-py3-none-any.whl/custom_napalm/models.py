from typing import Literal
from typing_extensions import TypedDict

VALID_INVENTORY_TYPES = Literal[
    "fabric_module",
    "fan",
    "linecard",
    "optic",
    "psu",
    "re",
    "stack_cable",
    "stack_member",
    "uplink_module",
    "aoc",
    "dac",
]

InventoryDict = TypedDict(
    "InventoryDict",
    {
        "type": VALID_INVENTORY_TYPES,
        "subtype": str,
        "name": str,
        "part_number": str,
        "serial_number": str,
    },
)
