import logging
import os

from .util import log_command_output

logger = logging.getLogger("kion-cli")

DEFAULT_CONFIG_FILE = os.path.join(str(os.getenv("HOME")), ".config", "kion.yml")


def update_kion_cli_password(config_file: str) -> None:
    if not os.path.exists(config_file):
        logger.error(f"kion cli config file {config_file} does not exist")
        return

    password = log_command_output(logger, ["op", "read", "op://Private/CMS EUA/password"])

    new_lines = []
    with open(config_file) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("  password:"):
                line = f"  password: {password}"
            new_lines.append(line)

    with open(config_file, "w") as f:
        f.write("\n".join(new_lines))
