import datetime
import logging
import random

logger = logging.getLogger("noop")


def run_noop():
    now = datetime.datetime.now()
    nlines = random.randint(2, 5)
    for i in range(1, nlines):
        logger.info(f"Message {i} from run at {now}")

    if random.choice([0, 1]):
        msg = f"Faking error for run at {now}"
        logger.error(msg)
        raise Exception(msg)
