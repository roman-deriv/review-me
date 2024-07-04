import logging
import os

LOG_FILE = os.environ.get("LOGFILE", "default_logfile.log")


def _init_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    log.addHandler(file_handler)
    log.addHandler(console_handler)

    return log


class LogFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith(__name__)


log = _init_logger()
