import logging
import os

from honcho.config import LOG_DIR, LOG_LEVEL, LOG_FILENAME, LOG_FORMATTER

logging_initialized = False


def init_logging(log_level=LOG_LEVEL, directory=LOG_DIR):
    global logging_initialized
    if not logging_initialized:
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        add_console_logging(root_logger, log_level)
        if directory is not None:
            add_file_logging(root_logger, log_level, directory)

        logging_initialized = True


def add_console_logging(logger, level):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = LOG_FORMATTER
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def add_file_logging(logger, level, directory=LOG_DIR, filename=LOG_FILENAME):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(directory, filename), maxBytes=1000000, backupCount=20
    )

    file_handler.setFormatter(LOG_FORMATTER)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
