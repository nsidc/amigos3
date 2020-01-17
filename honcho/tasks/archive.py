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


def archive_filepaths(
    filepaths, prefix=None, postfix=None, output_directory=ARCHIVE_DIR
):
    name = datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
    if prefix is not None:
        name = prefix + '_' + name
    if postfix is not None:
        name += '_' + postfix
    name += '.tgz'
    output_filepath = os.path.join(output_directory, name)
    make_tarfile(output_filepath, filepaths)

    return output_filepath


def archive_data():
    logger.debug('Archiving data')
    for tag in DATA_TAGS:
        data_dir = DATA_DIR(tag)
        filenames = os.listdir(data_dir)
        if filenames:
            filepaths = [os.path.join(data_dir, filename) for filename in filenames]
            logger.debug('Archiving files for {0}'.format(tag))
            archive_filepaths(filepaths, postfix=tag)
        else:
            logger.debug('Nothing to archive for {0}'.format(tag))


def archive_logs():
    logger.debug('Archiving data')
    filenames = os.listdir(LOG_DIR)
    if filenames:
        filepaths = [os.path.join(LOG_DIR, filename) for filename in filenames]
        logger.debug('Archiving logs')
        archive_filepaths(filepaths, postfix='LOG')
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


if __name__ == '__main__':
    execute()
