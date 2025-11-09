import argparse
from pprint import pprint

from napalm import get_network_driver

from custom_napalm import PLATFORM_MAP
from custom_napalm.base import SCBaseDriver
from custom_napalm.utils import configure_logging, LOG_LEVELS, get_from_args_or_env

# list of getters to run
GETTERS = [attr for attr in SCBaseDriver.__dict__ if attr.startswith("get")]

cred_args = {"sc_username": True, "sc_password": True}


def main():
    parser = argparse.ArgumentParser(
        description="""
Run a specific sc_napalm "getter" against a device.
"""
    )
    parser.add_argument("device", help="device hostname or IP address")
    parser.add_argument(
        "sc_napalm_platform",
        choices=PLATFORM_MAP,
        help="The platform of this device",
    )
    parser.add_argument(
        "cmd",
        choices=GETTERS,
        help="The getter command to run against this device",
    )
    parser.add_argument("--ssh-cfg", help="Use SSH config file to connect", type=str)
    log_args = parser.add_mutually_exclusive_group()
    log_args.add_argument(
        "-l", "--log-level", help="Set log level for sc_napalm only", choices=LOG_LEVELS
    )
    log_args.add_argument(
        "-L", "--LOG-LEVEL", help="set global log level", choices=LOG_LEVELS
    )
    parser.add_argument(
        "--logfile",
        type=str,
        help="Save logging to a file (specified by name) instead of to stdout",
    )

    for cred_arg in cred_args:
        parser.add_argument(f"--{cred_arg}", help="Specify credentials")
    args = parser.parse_args()

    log_level = args.log_level if args.log_level else args.LOG_LEVEL
    if log_level:
        configure_logging(
            log_level,
            log_globally=bool(args.LOG_LEVEL),
            log_file=args.logfile,
            log_to_console=not (bool(args.logfile)),
        )

    creds = {
        cred: get_from_args_or_env(cred, args, required=reqd)
        for cred, reqd in cred_args.items()
    }
    Driver = get_network_driver(args.sc_napalm_platform)

    # setting up connection details
    optional_args = {"look_for_keys": False}
    if args.ssh_cfg:
        optional_args = {"ssh_config_file": args.ssh_cfg}

    with Driver(
        args.device,
        creds["sc_username"],
        creds["sc_password"],
        timeout=60,
        optional_args=optional_args,
    ) as conn:
        result = getattr(conn, args.cmd)()
        pprint(result)


if __name__ == "__main__":
    main()
