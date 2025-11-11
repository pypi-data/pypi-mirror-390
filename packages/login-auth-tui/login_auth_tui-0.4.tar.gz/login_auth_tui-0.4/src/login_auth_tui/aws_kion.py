# This program is used to get AWS CLI credentials from kion and
# save them to your aws configuration. It assumes you are already
# connected to zscaler, and will likely fail in strange and
# unusual ways if you aren't. Ideally, you would run this from a
# cron/otherwise scheduled job to keep things updated.
import configparser
import datetime
import json
import logging
import os
import shutil
import subprocess  # nosec: B404 this is all trusted inputs

DEFAULT_AWS_CREDENTIALS = os.path.join(os.getenv("HOME"), ".aws", "credentials")  # type: ignore
DEFAULT_KION_SOURCE_CONFIG = os.path.join(os.getenv("HOME"), ".config", "kion.yml")  # type: ignore

logger = logging.getLogger("aws-kion")


def creds_need_update(creds_file_path: str, profile_name: str) -> bool:
    """Inspect the credentials we currently have to see if they
    really need updated.
    """
    logger.info(f"Checking {creds_file_path} to see if update is necessary")
    config = configparser.ConfigParser()
    config.read(creds_file_path)

    if profile_name not in config.sections():
        logger.debug(f"Profile [{profile_name}] does not exist, forcing update.")
        return True

    expiration = config[profile_name].get("expiration")
    if not expiration:
        logger.debug(f"No expiration date found for [{profile_name}], forcing update.")
        return True

    expiration_time = datetime.datetime.fromisoformat(expiration)
    now = datetime.datetime.now(datetime.UTC)
    logger.debug(f"Expiration={expiration_time.utctimetuple()}")
    logger.debug(f"Now={now.utctimetuple()}")
    if expiration_time <= (now + datetime.timedelta(minutes=10)):
        # Assume we're running no less than every 10 minutes
        logger.debug(f"Credentials for [{profile_name}] expire in under 10 minutes. Updating.")
        return True

    logger.debug(
        f"Credentials for [{profile_name}] are still good for at least 10 minutes. Not updating."
    )
    return False


def replace_kion_yaml(kion_yaml_path: str) -> None:
    """Copy our template kion cli config to the blessed
    kion location.
    """
    destination_yaml = os.path.join(
        os.getenv("HOME"),  # type: ignore
        ".kion.yml",
    )  # kion cli is inflexible
    if kion_yaml_path == destination_yaml:
        logger.debug("Kion yaml is sourced from the expected location, not copying.")
        return

    logger.debug(f"Copying {kion_yaml_path} -> {destination_yaml}")
    shutil.copyfile(kion_yaml_path, destination_yaml)


def update_aws_credentials(
    creds_file_path: str, profile_name: str, aws_creds: dict[str, str]
) -> None:
    """Given the new access key, secret key, and session token, save
    them for the named profile in the file indicated.
    """
    logger.info(f"Updating credentials in {creds_file_path}")
    # Initialize ConfigParser and read the credentials file
    config = configparser.ConfigParser()
    config.read(creds_file_path)

    # Ensure the profile exists in the credentials file, create it if missing
    if profile_name not in config.sections():
        logger.debug(f"Adding section {profile_name}")
        config.add_section(profile_name)

    # Update the profile with new credentials
    config[profile_name]["aws_access_key_id"] = aws_creds["AccessKeyId"]
    config[profile_name]["aws_secret_access_key"] = aws_creds["SecretAccessKey"]
    config[profile_name]["aws_session_token"] = aws_creds["SessionToken"]
    config[profile_name]["expiration"] = aws_creds["Expiration"]

    # Write the updated configuration back to the file
    with open(creds_file_path, "w") as creds_file:
        config.write(creds_file)

    logger.info(f"Credentials for profile [{profile_name}] updated successfully.")


def get_new_aws_credentials(
    favourite: str,
    kion: str = "/opt/homebrew/bin/kion",
) -> dict[str, str]:
    """Retrieve new AWS CLI credentials from kion using the CLI."""
    logger.info("Retrieving AWS credentials from kion")
    json_output = subprocess.check_output([kion, "favorite", "--credential-process", favourite])
    logger.debug(f"New credentials: {json_output}")
    return json.loads(json_output)


def aws_kion(
    profile: str, credentials: str, favourite: str, kion_yaml: str, kion_bin: str
) -> None:
    logger.debug(f"Profile: {profile}")
    logger.debug(f"Credentials File: {credentials}")
    logger.debug(f"Kion Favorite: {favourite}")
    logger.debug(f"Kion YAML: {kion_yaml}")

    try:
        if not creds_need_update(credentials, profile):  # type: ignore
            logger.info("Credentials have not yet expired. Not updating.")
            return

        replace_kion_yaml(kion_yaml)  # type: ignore
        aws_creds = get_new_aws_credentials(favourite, kion=kion_bin)  # type: ignore
        update_aws_credentials(credentials, profile, aws_creds)  # type: ignore
    except Exception:
        logger.exception("Exception occurred during update")
        raise
