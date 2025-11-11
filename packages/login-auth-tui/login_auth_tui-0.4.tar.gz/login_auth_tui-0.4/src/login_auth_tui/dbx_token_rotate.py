import configparser
import datetime
import json
import logging
import os
import shutil
import time
import typing

from .util import log_command_output

logger = logging.getLogger("dbx")

HOMEDIR = os.getenv("HOME")
TEN_DAYS_MS = 10 * 24 * 60 * 60 * 1000
NINETY_DAYS_S = int((TEN_DAYS_MS / 1000) * 9)


def run_dbx(profile: str, *args) -> str:
    subprocess_args = ["databricks", "--profile", profile, "-o", "json"] + list(args)
    logger.info(f"Run {' '.join(subprocess_args)}")
    return log_command_output(logger, subprocess_args)


def create_new_token(profile: str) -> str:
    logger.info(f"Creating new token for {profile}")
    today = str(datetime.date.today())
    new_token_json = run_dbx(
        profile,
        "tokens",
        "create",
        "--comment",
        f"dbx cli {today}",
        "--lifetime-seconds",
        str(NINETY_DAYS_S),
    )
    new_token = json.loads(new_token_json)

    return new_token["token_value"]


def delete_old_token(profile: str, token_id: str) -> None:
    logger.info(f"Deleting old token {token_id} for profile {profile}")
    run_dbx(profile, "tokens", "delete", token_id)


def overwrite_dbx_config(
    dbxcfg: str,
    cp: configparser.ConfigParser,
    profile: str,
    aliases: typing.Iterable[str],
    new_token: str,
) -> None:
    logger.info(f"Updating config file for profile {profile} (alias={aliases})")
    cp[profile]["token"] = new_token
    cp[profile]["nwgh-last-update"] = str(datetime.date.today())
    if aliases:
        for alias in aliases:
            cp[alias]["token"] = new_token
    with open(f"{dbxcfg}.new", "w") as f:
        cp.write(f)
    shutil.copyfile(dbxcfg, f"{dbxcfg}.old")
    shutil.move(f"{dbxcfg}.new", dbxcfg)


def manage_dbx_tokens(profile: str, aliases: typing.Iterable[str], force: bool) -> None:
    dbxcfg = os.path.join(str(os.getenv("HOME")), ".databrickscfg")
    if not os.path.exists(dbxcfg):
        raise Exception(f"Databricks config file {dbxcfg} does not exist")

    cp = configparser.ConfigParser()
    cp.read(dbxcfg)
    if profile not in cp:
        raise Exception(f"Databricks config does not have profile {dbxcfg}")

    json_result = run_dbx(profile, "tokens", "list")
    tokens = json.loads(json_result)
    if len(tokens) != 1:
        raise Exception(
            f"This script does not work with {len(tokens)} tokens! There can be only one."
        )

    now_ms = int(time.time()) * 1000
    if force or (tokens[0]["expiry_time"] - now_ms <= TEN_DAYS_MS):
        new_token = create_new_token(profile)
        overwrite_dbx_config(dbxcfg, cp, profile, aliases, new_token)
        delete_old_token(profile, tokens[0]["token_id"])
    else:
        logger.info(f"Token for {profile} is still ok, not rotating")
