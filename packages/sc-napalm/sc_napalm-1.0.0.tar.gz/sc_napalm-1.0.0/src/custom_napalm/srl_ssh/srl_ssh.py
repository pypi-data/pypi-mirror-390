from typing import Optional, Dict
from napalm.base import NetworkDriver


class NokiaSRLSSHDriver(NetworkDriver):
    """
    Netmiko based Nokia SRL driver :(
    """

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        timeout: int = 60,
        optional_args: Optional[Dict] = None,
    ) -> None:
        if optional_args is None:
            optional_args = {}
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

    def open(self):
        self.device = self._netmiko_open("nokia_srl")

    def close(self):
        self._netmiko_close()

    def send_command(self, cmd: str) -> str:
        """
        Sends command with netmiko and returns the result
        """
        return self.device.send_command(cmd)

    def get_config(self, retrieve="all", full=False, sanitized=False, format="text"):
        result = {"startup": "", "candidate": "", "running": ""}
        if retrieve in ["all", "running"]:
            result["running"] = self.send_command("info from running flat")
        if retrieve in ["all", "startup"]:
            result["startup"] = self.send_command("info from startup flat")
        if retrieve in ["all", "candidate"]:
            result["candidate"] = self.send_command("info from candidate flat")
        return result
