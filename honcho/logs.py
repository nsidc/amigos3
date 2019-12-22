import logging

from honcho.config import LOG_LEVEL, LOG_FORMATTER

logging_initialized = False


def init_logging(log_level=LOG_LEVEL):
    global logging_initialized
    if not logging_initialized:
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        add_console_logging(root_logger, log_level)
        logging_initialized = True


def add_console_logging(logger, level):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(LOG_FORMATTER)
    logger.addHandler(stream_handler)


init_logging()
