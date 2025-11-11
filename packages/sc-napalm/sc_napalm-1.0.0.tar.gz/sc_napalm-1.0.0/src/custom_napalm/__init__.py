from .iosxr import SCIOSXR
from .junos import SCJunOS
from .nxos import SCNXOS
from .sros import SCNokiaSROSDriver
from .srl_ssh import NokiaSRLSSHDriver
from .srl import SCNokiaSRLDriver
from .eos import SCEOSDriver
from .nos import SCNOSDriver

PLATFORM_MAP = {
    "iosxr": SCIOSXR,
    "nxos": SCNXOS,
    "junos": SCJunOS,
    "sros": SCNokiaSROSDriver,
    "srl_ssh": NokiaSRLSSHDriver,
    "srl": SCNokiaSRLDriver,
    "eos": SCEOSDriver,
    "nos": SCNOSDriver,
}


def get_network_driver(platform: str):
    """
    Returns network driver based on platform string.
    """
    for valid_platform, driver in PLATFORM_MAP.items():
        if valid_platform == platform:
            return driver

    raise NotImplementedError(f"Unsupported platform {platform}")
