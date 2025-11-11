import logging
import logging.handlers
import os
import subprocess  # nosec
import sys

HOME = str(os.getenv("HOME"))


def configure_logging(log: str, level: str) -> None:
    if log in ("stdout", "-"):
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.handlers.RotatingFileHandler(
            log,
            backupCount=1,
            maxBytes=1024 * 1024,
        )
    try:
        log_level = logging.getLevelNamesMapping()[level]
    except Exception:
        raise ValueError(f"Unhandled log level {level}")
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        level=log_level,
        handlers=[handler],
    )


def log_command(
    logger: logging.Logger, command: list[str], **kwargs
) -> subprocess.CompletedProcess:
    logger.info(f"Run {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, **kwargs)  # nosec
    logger.info("--- BEGIN PROCESS STDOUT ---")
    for line in result.stdout.decode("utf-8").strip().split("\n"):
        logger.info(line)
    logger.info("--- END PROCESS STDOUT ---")
    logger.info("--- BEGIN PROCESS STDERR ---")
    for line in result.stderr.decode("utf-8").strip().split("\n"):
        logger.error(line)
    logger.info("--- END PROCESS STDERR ---")
    return result


def log_command_output(logger: logging.Logger, command: list[str], **kwargs) -> str:
    logger.info(f"Run: {' '.join(command)}")
    output = subprocess.check_output(command, **kwargs)  # nosec
    return output.decode("utf-8").strip()
