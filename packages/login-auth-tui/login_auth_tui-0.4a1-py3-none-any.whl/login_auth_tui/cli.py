import configparser
import copy
import logging
import os
import sqlite3
import sys
import time

import click
from click.core import ParameterSource as Source

from .aws_kion import DEFAULT_AWS_CREDENTIALS, DEFAULT_KION_SOURCE_CONFIG, aws_kion
from .aws_mfa import aws_mfa
from .dbx_token_rotate import manage_dbx_tokens
from .kion_auth_password import update_kion_auth_password
from .kion_cli_password import DEFAULT_CONFIG_FILE, update_kion_cli_password
from .tui import run_tui
from .tui_bootstrap import bootstrap_tui_config
from .util import configure_logging, log_command

TWELVE_HOURS = 12 * 60 * 60
DEFAULT_LOG = os.path.join(str(os.getenv("HOME")), ".logs", "login-auth.log")


class CliArgs:
    __slots__ = ["force", "log", "level"]

    def __init__(self):
        self.force = False
        self.log = DEFAULT_LOG
        self.level = "INFO"


@click.group()
@click.version_option()
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force update regardless of last update time (only aws, batch, and dbx).",
)
@click.option(
    "--log",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, allow_dash=True),
    default=DEFAULT_LOG,
    help="File to log to ('-' for stdout).",
)
@click.option(
    "--level",
    type=click.Choice([k for k in logging.getLevelNamesMapping().keys() if k != "NOTSET"]),
    default="INFO",
    help="Logging level to use.",
)
@click.pass_context
def cli(ctx: click.Context, force: bool, log: str, level: str):
    """Run authentication useful when developing on DataConnect."""
    ctx.ensure_object(CliArgs)
    ctx.obj.force = force
    ctx.obj.log = log
    ctx.obj.level = level


def login_auth(force: bool, conn: sqlite3.Connection) -> None:
    # Now that we hold an exclusive lock on the config, see if we actually need
    # to do anything.
    last_update = conn.execute("SELECT * FROM last_update").fetchone()[0]
    now = time.time()
    if last_update < (now - TWELVE_HOURS):
        logging.info("More than twelve hours since last update.")
    elif force:
        logging.info("Running due to force")
    else:
        logging.info("Not running; auth does not need to be updated")
        return

    res = conn.execute("SELECT * FROM config")
    config = dict(zip([r[0] for r in res.description], res.fetchone()))

    if config["wait"]:
        logging.info(f"Waiting {config['wait']} seconds for boot...")
        time.sleep(config["wait"])

    if config["ssh_add"]:
        logging.info("Adding SSH keys...")
        env = copy.deepcopy(os.environ)
        args = ["/usr/bin/ssh-add"]
        if sys.platform == "darwin":
            env["APPLE_SSH_ADD_BEHAVIOR"] = "yes"
            args.append("-A")
        log_command(logging.getLogger(), args, env=env)

    success = True
    res = conn.execute("SELECT * FROM aws_profiles")
    aws_profiles = [r[0] for r in res.fetchall()]
    for aws_profile in aws_profiles:
        logging.info(f"Authenticating AWS profile {aws_profile}")
        try:
            aws_mfa(aws_profile, force)
        except Exception:
            logging.exception(f"Exception running AWS MFA {aws_profile}")
            success = False

    res = conn.execute("SELECT * FROM dbx_profiles")
    for row in res.fetchall():
        profile, alias = row
        logging.info(f"Rotating DBX token {profile} (alias={alias})")
        try:
            manage_dbx_tokens(profile, [alias], force)
        except Exception:
            logging.exception(f"Exception rotating DBX token {profile}")
            success = False

    kion_auth_config_file = config["kion_auth_config_file"]
    if kion_auth_config_file:
        logging.info("Update kion-auth config file with current password")
        update_kion_auth_password(kion_auth_config_file)

    kion_cli_config_file = config["kion_cli_config_file"]
    if kion_cli_config_file:
        logging.info("Update kion cli config file with current password")
        update_kion_cli_password(kion_cli_config_file)

    if success:
        logging.info("Success!")
        conn.execute(f"UPDATE last_update SET tstamp = {int(now)}")  # nosec
    else:
        logging.info("Failed")


@cli.command("batch")
@click.option("--background", is_flag=True, default=False, help="Run in the background.")
@click.option(
    "--config",
    type=click.Path(dir_okay=False, exists=True, resolve_path=True),
    default=os.path.join(str(os.getenv("HOME")), ".config", "login-auth.sqlite"),
    help="Path to configuration database.",
)
@click.pass_context
def login_auth_main(ctx: click.Context, background: bool, config: str) -> None:
    """Run all the login management in one batch."""
    if background:
        # TODO - run in the background
        pid = os.fork()
        if pid != 0:
            # This is the parent, we done
            return

        # This is the child, detach from the parent
        os.setpgrp()

    configure_logging(ctx.obj.log, ctx.obj.level)

    conn = sqlite3.connect(config)
    conn.execute("BEGIN EXCLUSIVE TRANSACTION")

    try:
        login_auth(ctx.obj.force, conn)
    except Exception:
        logging.exception("Exception doing login_auth")
        conn.execute("ROLLBACK")
        raise
    else:
        logging.info("Commit transaction")
        conn.execute("COMMIT")


@cli.command("aws")
@click.argument("profile")
@click.pass_context
def aws_mfa_main(ctx: click.Context, profile: str) -> None:
    """Run AWS MFA process.

    PROFILE the AWS profile to run the MFA process for.
    """
    configure_logging(ctx.obj.log, ctx.obj.level)

    aws_mfa(profile, ctx.obj.force)


@cli.command("dbx")
@click.option("--alias", multiple=True, help="Other profiles that are aliases.")
@click.argument("profile")
@click.pass_context
def dbx_token_rotate_main(ctx: click.Context, alias: tuple[str], profile: str) -> None:
    """Rotate Databricks API token.

    PROFILE the Databricks configuration profile to rotate the API token for.
    """
    configure_logging(ctx.obj.log, ctx.obj.level)

    manage_dbx_tokens(profile, alias, ctx.obj.force)


@cli.command("kion-auth")
@click.option(
    "--file",
    type=click.Path(exists=True, dir_okay=False, writable=True, resolve_path=True),
    default=os.path.join(str(os.getenv("HOME")), ".config", "kion-auth.ini"),
    help="Path of kion-auth configuration file.",
)
@click.pass_context
def update_kion_auth_password_main(ctx: click.Context, file: str) -> None:
    """Update the password used by kion-auth from 1Password."""
    configure_logging(ctx.obj.log, ctx.obj.level)

    update_kion_auth_password(file)


@cli.command("kion-cli")
@click.option(
    "--file",
    type=click.Path(exists=True, dir_okay=False, writable=True, resolve_path=True),
    default=DEFAULT_CONFIG_FILE,
    help="Path of kion cli configuration file.",
)
@click.pass_context
def update_kion_cli_password_main(ctx: click.Context, file: str) -> None:
    """Update the password used by the kion cli from 1Password."""
    configure_logging(ctx.obj.log, ctx.obj.level)

    update_kion_cli_password(file)


@cli.command("tui")
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, writable=True, resolve_path=True),
    default=os.path.join(str(os.getenv("HOME")), ".config", "login_auth.yml"),
    help="Path of TUI configuration file.",
)
@click.pass_context
def tui(ctx: click.Context, config: str) -> None:
    """Run the TUI for authentication processes."""
    configure_logging(ctx.obj.log, ctx.obj.level)
    run_tui(config)


@cli.command("tui-bootstrap")
@click.option(
    "--in-config",
    type=click.Path(dir_okay=False, exists=True, resolve_path=True),
    default=os.path.join(str(os.getenv("HOME")), ".config", "login-auth.sqlite"),
    help="Path to configuration database.",
)
@click.option(
    "--out-config",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    default=os.path.join(str(os.getenv("HOME")), ".config", "login_auth.yml"),
    help="Path of TUI configuration file.",
)
@click.pass_context
def tui_bootstrap(ctx: click.Context, in_config: str, out_config: str) -> None:
    """Bootstrap the tui configuration from the batch configuration."""
    configure_logging(ctx.obj.log, ctx.obj.level)
    if os.path.exists(out_config) and not ctx.obj.force:
        raise ValueError(f"Not overwriting existing TUI config {out_config}")
    bootstrap_tui_config(in_config, out_config)


@cli.command("aws-kion")
@click.option(
    "--credentials",
    help="Location of AWS Credentials file",
    default=DEFAULT_AWS_CREDENTIALS,
    show_default=True,
)
@click.option(
    "--config",
    help="Path of configuration file",
    default=os.path.join(os.getenv("HOME"), ".config", "aws-token-updater.ini"),  # type: ignore
    show_default=True,
)
@click.option(
    "--kion-yaml",
    help="Path of kion configuration file",
    default=DEFAULT_KION_SOURCE_CONFIG,
    show_default=True,
)
@click.option(
    "--kion-bin",
    help="Path to kion executable",
    default="/opt/homebrew/bin/kion",
)
@click.option("--profile", help="Name of AWS profile to update")
@click.option("--favourite/--favorite", help="Name of kion favourite to use")
@click.pass_context
def aws_kion_main(
    ctx,
    credentials: str,
    config: str,
    kion_yaml: str,
    kion_bin: str,
    profile: str,
    favourite: str,
):
    configure_logging(ctx.obj.log, ctx.obj.level)

    # Read configuration from the file if it exists, otherwise start
    # with an empty configuration and hope the user used the CLI args
    # Configuration prefers the CLI arguments if given, otherwise it
    # takes information from the config file.
    if os.path.exists(config):
        c = configparser.ConfigParser()
        c.read(config)
        cfg = c["aws_token_updater"]
    else:
        cfg = {}

    if not profile:
        profile = cfg.get("profile")  # type: ignore

    if not favourite:
        favourite = cfg.get("favourite")  # type: ignore

    # Just like the log destination file, we only want to override
    # what came in from the CLI args if what came in was the default
    if ctx.get_parameter_source("credentials") == Source.DEFAULT and cfg.get("credentials"):
        credentials = cfg.get("credentials")  # type: ignore

    # Just like the log destination file, we only want to override
    # what came in from the CLI args if what came in was the default
    if ctx.get_parameter_source("kion_yaml") == Source.DEFAULT and cfg.get("kion_yaml"):
        kion_yaml = cfg.get("kion_yaml")  # type: ignore

    # Just like the log destination file, we only want to override
    # what came in from the CLI args if what came in was the default
    if ctx.get_parameter_source("kion_bin") == Source.DEFAULT and cfg.get("kion_bin"):
        cfg.get("kion_bin")

    if not all([profile, credentials, favourite]):
        raise ValueError(
            "Missing one configuration. Ensure configurtion file exists or all arguments are passed"
        )

    aws_kion(profile, credentials, favourite, kion_yaml, kion_bin)
