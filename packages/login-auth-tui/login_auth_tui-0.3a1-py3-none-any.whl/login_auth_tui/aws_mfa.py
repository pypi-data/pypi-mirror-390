import configparser
import datetime
import logging
import os

from .util import log_command, log_command_output

logger = logging.getLogger("aws")

HOMEDIR = str(os.getenv("HOME"))


def credential_is_valid(profile: str) -> bool:
    now = datetime.datetime.now(datetime.UTC)

    p = configparser.ConfigParser()
    p.read(os.path.join(HOMEDIR, ".aws", "credentials"))

    then_s = p.get(profile, "expiration")
    then = datetime.datetime.strptime(f"{then_s} +0000", "%Y-%m-%d %H:%M:%S %z")

    if now < then:
        return True
    return False


def aws_mfa(profile: str, force: bool) -> None:
    logger.info(f"Running mfa process for {profile}")

    no_mfa_file = os.path.join(HOMEDIR, f".no-mfa-{profile}")
    if os.path.exists(no_mfa_file) and not force:
        logger.info("Not doing mfa due to temp file existing. (Removing the file.)")
        os.unlink(no_mfa_file)
        return

    if credential_is_valid(profile) and not force:
        logger.info("Not doing mfa due to credentials still valid.")
        return

    code = log_command_output(
        logger, ["op", "read", "op://Private/AWS/one-time password?attribute=totp"]
    )
    logger.info(f"Using {code} for {profile}")
    rval = log_command(
        logger,
        [f"{os.getenv('HOMEBREW_PREFIX')}/bin/aws", "mfa", profile],
        input=code.encode("utf-8"),
    ).returncode

    if rval != 0:
        # For some reason, recently, aws-mfa has been returning 1 even though
        # it successfully updates the tokens. So if it does return non-zero,
        # we need to check the credentials file itself to verify if it's a real
        # failure or not.
        logger.info("Warning: MFA seems to have failed by rval, checking expiration")
        if not credential_is_valid(profile):
            logger.error(f"Not rotating long-term keys due to MFA failure ({rval})")
            raise Exception("AWS MFA failure")

    logger.info("Rotating long-term keys")
    log_command(logger, ["aws", "rotate-iam-keys", f"{profile}-long-term"], check=True)
