import argparse
from pathlib import Path
import json

import custom_napalm
from mock_drivers import *

from pprint import pprint

PLATFORM_MAP = {
    "iosxr": MockIOSXR,
    "nxos": MockNXOS,
    "junos": MockJunos,
    #    "sros": SCNokiaSROSDriver,
    "srl": MockNokiaSRL,
    "eos": MockEOS,
}


def get_mock_driver(platform: str):
    """
    Returns network driver based on platform string.
    """
    for valid_platform, driver in PLATFORM_MAP.items():
        if valid_platform == platform:
            return driver

    raise NotImplementedError(f"Unsupported platform {platform}")


if __name__ == "__main__":
    MOCK_DATA_DIR = Path(__file__).parent / "mock_data"

    parser = argparse.ArgumentParser(
        description="""Generate mock output data based on raw router input saved in the mock_data directory"""
    )
    parser.add_argument("platform", choices=custom_napalm.PLATFORM_MAP)
    parser.add_argument("getter", type=str)
    parser.add_argument("test_name", type=str)
    parser.add_argument(
        "--save", action="store_true", help="Save result to test folder"
    )

    args = parser.parse_args()

    test_dir = MOCK_DATA_DIR / args.platform / args.getter / args.test_name

    folder = Path(test_dir)
    if not folder.exists():
        raise FileNotFoundError(f"No test folder {test_dir}")

    driver = get_mock_driver(args.platform)
    with driver(test_dir) as device:
        result = getattr(device, args.getter)()

    pprint(result)

    if args.save:
        with open(f"{test_dir}/expected_result.json", "w", encoding="utf-8") as fh:
            fh.write(json.dumps(result, indent=4))
