import logging

from settings import LOGGING_LEVEL

_log_format = "%(asctime)s [%(levelname)s] >>> %(message)s"
_time_format = "%H:%M:%S"


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOGGING_LEVEL)
    stream_handler.setFormatter(logging.Formatter(fmt=_log_format, datefmt=_time_format))

    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(get_stream_handler())

    return logger
