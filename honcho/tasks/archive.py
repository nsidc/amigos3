import os
from logging import getLogger
from datetime import datetime

from honcho.config import (
    LOG_DIR,
    DATA_DIR,
    DATA_TAGS,
    ARCHIVE_DIR,
    TIMESTAMP_FILENAME_FMT,
)
from honcho.util import make_tarfile, clear_directory
from honcho.tasks.common import task


logger = getLogger(__name__)


def archive_data():
    for tag in DATA_TAGS:
        if os.listdir(DATA_DIR(tag)):
            logger.debug('Archiving {0}'.format(tag))
            name = tag + '_' + datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tgz'
            output_filepath = os.path.join(ARCHIVE_DIR, name)
            make_tarfile(output_filepath, DATA_DIR(tag))
        else:
            logger.debug('No data to archive for {0}'.format(tag))


def archive_logs():
    logger.debug('Archiving logs')
    name = 'LOG_' + datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tgz'
    output_filepath = os.path.join(ARCHIVE_DIR, name)
    make_tarfile(output_filepath, LOG_DIR)


@task
def execute():
    archive_data()
    archive_logs()

    logger.debug('Cleaning up')
    for tag in DATA_TAGS:
        clear_directory(DATA_DIR(tag))
    clear_directory(LOG_DIR)
