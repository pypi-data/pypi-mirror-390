# # pylint: disable=no-member
from typing import List
import re
import logging

from napalm.junos import JunOSDriver
from napalm.base.models import LLDPNeighborDict, ConfigDict
from ..models import InventoryDict
from ..base import SCBaseNetconfDriver


from . import junos_views

logger = logging.getLogger(__name__)

XCVR_DESC_TO_INTERFACE_PREFIX = {
    r"100GBASE-": "et-",
    r"QSFP": "et-",
    r"SFP28": "et-",
    r"SFP\+": "xe-",
    r"SFP-": "ge-",
    r"CFP-": "et-",
    r"(UNKNOWN|UNSUPPORTED)": "ge-",  # default
}

DEFAULT_ARP_AGING_TIMER = 1200


class SCJunOS(JunOSDriver, SCBaseNetconfDriver):
    """
    Junos parser
    """

    netmiko_host_type = "juniper_junos"

    # mapping of inventory name regex to their netbox types
    INVENTORY_TO_TYPE = {
        r"Fan Tray": "fan",
        r"(PIC|MIC|FPC)": "linecard",
        r"Xcvr": "optic",
        r"(PEM|Power Supply)": "psu",
        r"Routing Engine": "re",
        # don't care about these inventory items
        r"(CPU|PDM|FPM|Midplane|CB|SFB|TIB)": None,
    }

    def _get_junos_inventory_type(self, name: str, model_number: str) -> str:
        """
        Maps the name and part number of the Junos inventory item to its type
        """
        # "Xcvr" parts are always optics
        if name.startswith("Xcvr"):
            return "optic"

        # non-optic parts should always have a model number, if not
        # we don't care about them
        if not (model_number):
            return None

        # EX switches and virtual chassis save their vc members and uplink modules
        # as FPC X and PIC X - we want to classify those correctly
        if re.match(r"EX[234]", model_number):
            if re.search(r"FPC \d+", name):
                return "stack-member"

            if re.search(r"PIC \d+", name):
                return None

        # uplink modules are also saved under PIC X, must classify based
        # on their model number
        if re.match(r"EX-UM", model_number):
            return "uplink-module"

        # otherwise we want to pattern-match based on the INVENTORY_TO_TYPE
        # dictionary
        return self._get_inventory_type(name)

    def _get_xcvr_interface_prefix(self, xcvr_desc: str) -> str:
        """
        Maps xcvr description from "show chassis hardware" to
        interface prefix
        """
        for pattern, prefix in XCVR_DESC_TO_INTERFACE_PREFIX.items():
            if re.match(pattern, xcvr_desc):
                return prefix

        raise ValueError(f"{self.hostname}: Unknown xcvr type {xcvr_desc}")

    def _get_mod_number(self, mod_name: str) -> str:
        """
        Strips out "FPC|MIC|PIC" from a module name seen in "show chassis hardware"
        """
        return re.sub(r"(MIC|PIC|FPC) ", "", mod_name)

    def _get_inventory_part_number(self, item: any) -> str:
        """
        Extracts the part number from an inventory item
        which, depending on the specific item, is stashed in
        the part number, model number, or description field
        """
        if item.model_number and item.model_number != "model-number":
            return item.model_number
        return item.part_number

    def _save_inventory_item(
        self, output: list, item: any, parent: str = None, grandparent: str = None
    ) -> bool:
        """
        Extracts data from a particular inventory item object.
        Returns whether we care aobut this item or not (so we know whether or not)
        to loop over its children
        """
        # skip builtin types, or parts without model numbers that aren't transcievers
        if item.part_number == "BUILTIN":
            return False

        # get inventory type based on item name and P/N
        inv_type = self._get_junos_inventory_type(item.name, item.model_number)

        if not inv_type:
            return False

        # for transcievers, change the name from Xcvr X to be the junos interface name
        # note that we expect transcievers to always be at the sub-sub module level
        # and thus to have a grandparent and parent
        m = re.search(r"Xcvr (\d+)", item.name)
        if m:
            if not (grandparent or parent):
                raise ValueError(
                    f"{self.hostname}: No MIC and PIC found for {item.name}"
                )
            prefix = self._get_xcvr_interface_prefix(item.description)

            item_name = f"{prefix}{self._get_mod_number(grandparent)}/{self._get_mod_number(parent)}/{m.group(1)}"

        # for sub-linecards (mics or pics) we want to prepend the parent to the item name
        elif parent:
            item_name = f"{parent} {item.name}"
        else:
            item_name = item.name

        output.append(
            {
                "type": inv_type,
                "name": item_name,
                "subtype": item.description,
                "part_number": self._get_inventory_part_number(item),
                "serial_number": item.serial_number,
            }
        )

        return True

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> ConfigDict:
        """
        pulling running config via ssh sow we can have it in 'display set' format.
        """
        if format != "text":
            return super().get_config(
                retrieve=retrieve, full=full, sanitized=sanitized, format=format
            )

        config = {"startup": "", "running": "", "candidate": ""}

        with self.ssh_conn() as ssh_device:
            config["running"] = ssh_device.send_command(
                "show configuration | display set"
            )

        return config

    def get_lldp_neighbors(self) -> LLDPNeighborDict:
        """
        Overrides napalm get_lldp_neighbors so that we actually get the remote
        interface ID instead of the description.

        NAPALM's get_lldp_neighbors_detail gets this for us - note that to get this detail,
        you need to execute a command for each interface just like on the cli :(
        """
        neighs = super().get_lldp_neighbors_detail()
        output = {}
        for port, neighs in neighs.items():
            output[port] = []
            for neigh in neighs:
                output[port].append(
                    {
                        "hostname": neigh["remote_system_name"]
                        if neigh["remote_system_name"]
                        else neigh["remote_chassis_id"],
                        "port": neigh["remote_port"],
                    }
                )
        return output

    def get_inventory(self) -> List[InventoryDict]:
        """
        parses the get-chassis-inventory RPC call, which maps to "show chassis hardware"
        """
        result = junos_views.junos_inventory(self.device).get()

        output = []
        for chassis in dict(result).values():
            # note that the chassis model and s/n are at this level, but
            # that doesn't count as an 'inventory item' so we're ignoring it

            # saving modules, sub-modules and sub-sub modules
            for module in dict(chassis.modules).values():
                self._save_inventory_item(output, module)

                for sub_module in dict(module.sub_modules).values():
                    self._save_inventory_item(output, sub_module, parent=module.name)

                    for sub_sub_module in dict(sub_module.sub_sub_modules).values():
                        self._save_inventory_item(
                            output,
                            sub_sub_module,
                            parent=sub_module.name,
                            grandparent=module.name,
                        )

        return output
