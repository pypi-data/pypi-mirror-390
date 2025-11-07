from typing import Union
import logging
import sys
import argparse
from decouple import config
from os import getenv

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.WARNING,
    "CRITICAL": logging.CRITICAL,
}
LOG_FORMAT = "%(asctime)-15s  %(levelname)8s %(name)s %(message)s"


def configure_logging(
    log_level: Union[int, str],
    log_globally: bool = False,
    log_file: str = None,
    log_to_console: bool = False,
):
    """
    Configures logging for the module, or globally as indicated by the input
    """

    if log_globally:
        logger = logging.getLogger()
    else:
        module_name = __name__.split(".")[0]
        logger = logging.getLogger(module_name)

    if isinstance(log_level, str):
        log_level = LOG_LEVELS[log_level.upper()]
    logger.setLevel(log_level)

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024 * 10, backupCount=20
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    if log_to_console:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(stdout_handler)


def get_from_args_or_env(
    cli_arg: str, parsed_args: argparse.Namespace = None, required=True
) -> str:
    """
    Pull a value from parsed arparse, if it's not there look for it
    in .env, and if it's not there, check the user's environment.
    """
    cli_arg = cli_arg.replace("-", "_")

    if getattr(parsed_args, cli_arg, False):
        return getattr(parsed_args, cli_arg)

    env_arg = cli_arg.upper()
    if config(env_arg, None):
        return config(env_arg)

    if getenv(env_arg):
        return getenv(env_arg)

    if required:
        raise ValueError(
            f"ERROR: Please provide {cli_arg} as cli input or set as {env_arg} environment variable"
        )
    return None
