import logging
import os

LOG_DIRECTORY = '/media/media/mmcblk0p1/logs'
LOG_FILENAME = 'system.log'
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


root_logger = logging.getLogger()


def init_logging(log_level=logging.INFO, directory=None):
    root_logger.setLevel(log_level)
    add_console_logging(root_logger, log_level)
    if directory is not None:
        add_file_logging(root_logger, directory, log_level)


def add_console_logging(logger, level):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = FORMATTER
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def add_file_logging(
    logger, directory=LOG_DIRECTORY, filename=LOG_FILENAME, level=logging.INFO
):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_handler = logging.FileHandler(os.path.join(directory, filename))

    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
