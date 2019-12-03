import os
from ftplib import FTP
from logging import getLogger
from contextlib import closing
from datetime import datetime

from honcho.config import (
    LOG_DIR,
    GPIO,
    FTP_HOST,
    FTP_TIMEOUT,
    FTP_CONNECT_RETRIES,
    DATA_ROOT_DIR,
    DATA_DIR,
    DATA_TAGS,
    STAGED_UPLOAD_DIR,
    UPLOAD_DATA_TAGS,
    UPLOAD_CLEANUP,
    ARCHIVE_DIR,
)
from honcho.util import (
    get_creds,
    fail_gracefully,
    log_execution,
    file_size,
    make_tarfile,
    serialize_datetime,
    clear_directory,
)


logger = getLogger(__name__)


def archive_data():
    for tag in DATA_TAGS:
        name = tag + '_' + serialize_datetime(datetime.now()) + '.tgz'
        output_filepath = os.path.join(ARCHIVE_DIR, name)
        make_tarfile(output_filepath, DATA_DIR(tag))


def archive_logs():
    name = 'LOG_' + serialize_datetime(datetime.now()) + '.tgz'
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
