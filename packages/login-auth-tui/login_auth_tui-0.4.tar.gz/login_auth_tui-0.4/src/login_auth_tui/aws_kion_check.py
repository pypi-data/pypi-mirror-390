import logging
import subprocess

logger = logging.getLogger("aws-kion-check")


def aws_kion_check(profile: str) -> None:
    output = subprocess.check_output(["aws", "--profile", profile, "s3", "ls"])
    logger.debug("Output from aws s3 ls")
    logger.debug(output)
