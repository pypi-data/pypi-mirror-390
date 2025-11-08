import configparser
import logging
import os

from .util import log_command_output

logger = logging.getLogger("kion-auth")


def update_kion_auth_password(config_file: str) -> None:
    if not os.path.exists(config_file):
        logger.error(f"kion-auth config file {config_file} does not exist")
        return

    cp = configparser.ConfigParser()
    cp.read(config_file)

    if not cp.get("kion_auth", "password"):
        logger.info("Kion password is not defined, not updating")
        return

    password = log_command_output(logger, ["op", "read", "op://Private/CMS EUA/password"])
    cp["kion_auth"]["password"] = password

    with open(config_file, "w") as f:
        cp.write(f)
