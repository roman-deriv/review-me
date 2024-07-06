import logging
import os

LOG_FILE = os.environ.get("LOGFILE", "default_logfile.log")


def _init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


log = _init_logger()
