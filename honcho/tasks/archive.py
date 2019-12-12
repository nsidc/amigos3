import os
from logging import getLogger
from datetime import datetime

from honcho.config import (
    LOG_DIR,
    DATA_ROOT_DIR,
    DATA_DIR,
    DATA_TAGS,
    ARCHIVE_DIR,
    TIMESTAMP_FILENAME_FMT,
)
from honcho.util import fail_gracefully, log_execution, make_tarfile, clear_directory


logger = getLogger(__name__)


def archive_data():
    for tag in DATA_TAGS:
        name = tag + '_' + datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tgz'
        output_filepath = os.path.join(ARCHIVE_DIR, name)
        make_tarfile(output_filepath, DATA_DIR(tag))


def archive_logs():
    name = 'LOG_' + datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tgz'
    output_filepath = os.path.join(ARCHIVE_DIR, name)
    make_tarfile(output_filepath, LOG_DIR)


@fail_gracefully
@log_execution
def execute():
    logger.debug('Archiving data')
    archive_data()
    archive_logs()

    logger.debug('Cleaning up')
    clear_directory(DATA_ROOT_DIR)


if __name__ == "__main__":
    execute()
