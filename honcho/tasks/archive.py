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


def archive_filepaths(filepaths, prefix, output_directory=ARCHIVE_DIR):
    name = prefix + '_' + datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tgz'
    output_filepath = os.path.join(output_directory, name)
    make_tarfile(output_filepath, filepaths)


def archive_data():
    logger.debug('Archiving data')
    for tag in DATA_TAGS:
        data_dir = DATA_DIR(tag)
        filenames = os.listdir(data_dir)
        if filenames:
            filepaths = [os.path.join(data_dir, filename) for filename in filenames]
            logger.debug('Archiving files for {0}'.format(tag))
            archive_filepaths(filepaths, tag)
        else:
            logger.debug('Nothing to archive for {0}'.format(tag))


def archive_logs():
    logger.debug('Archiving data')
    filenames = os.listdir(LOG_DIR)
    if filenames:
        filepaths = [os.path.join(LOG_DIR, filename) for filename in filenames]
        logger.debug('Archiving logs')
        archive_filepaths(filepaths, prefix='LOGS')
    else:
        logger.debug('No logs to archive')


@task
def execute():
    archive_data()
    archive_logs()

    logger.debug('Cleaning up')
    for tag in DATA_TAGS:
        clear_directory(DATA_DIR(tag))
    clear_directory(LOG_DIR)
