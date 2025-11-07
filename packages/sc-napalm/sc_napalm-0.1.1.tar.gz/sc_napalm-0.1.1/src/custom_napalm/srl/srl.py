from napalm_srl import NokiaSRLDriver
from ..base import SCBaseDriver


class SCNokiaSRLDriver(NokiaSRLDriver, SCBaseDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing insecure connection for testing purposes
        """
        optional_args = optional_args if optional_args else {}
        optional_args["insecure"] = True
        optional_args["encoding"] = "JSON_IETF"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

    def get_inventory(self):
        path = {"/interface"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        interfaces = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        return interfaces
