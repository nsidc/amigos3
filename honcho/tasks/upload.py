import os
from ftplib import FTP
from logging import getLogger
from contextlib import closing
from datetime import datetime

from honcho.config import (
    GPIO,
    STAGED_UPLOAD_DIR,
    FTP_HOST,
    FTP_TIMEOUT,
    UPLOAD_CLEANUP,
    DATA_DIR,
    LOG_DIR,
    UPLOAD_DATA_TAGS,
)
from honcho.util import (
    get_creds,
    ensure_dirs,
    fail_gracefully,
    file_size,
    make_tarfile,
    serialize_datetime,
)
from honcho.core.gpio import powered


logger = getLogger(__name__)


def stage_path(path, prefix=None):
    name = os.path.basename(path) + '_' + serialize_datetime(datetime.now()) + '.tgz'
    if prefix is not None:
        name = prefix + '_' + name
    output_filepath = os.path.join(STAGED_UPLOAD_DIR, name)
    make_tarfile(output_filepath, path)


def stage_data():
    for i, tag in enumerate(UPLOAD_DATA_TAGS):
        stage_path(os.path.join(DATA_DIR, tag), i)


def stage_logs():
    for logfile in os.listdir(LOG_DIR):
        stage_path(os.path.join(LOG_DIR, logfile))


def upload_staged(clean=UPLOAD_CLEANUP):
    with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
        ftp.login(*get_creds(FTP_HOST))
        logger.debug('Logged in to {0}'.format(FTP_HOST))
        filenames = os.listdir(STAGED_UPLOAD_DIR)
        for filename in filenames:
            filepath = os.path.join(STAGED_UPLOAD_DIR, filename)
            with open(filepath, 'rb') as fi:
                logger.debug(
                    'Uploading {0} bytes: {1}'.format(file_size(filepath), filepath)
                )
                ftp.storbinary('STOR {0}'.format(filename), fi)
                logger.debug('Success')

            if UPLOAD_CLEANUP:
                logger.debug('Removing {0}'.format(filepath))
                os.remove(filepath)


@fail_gracefully
def execute():
    ensure_dirs([STAGED_UPLOAD_DIR])
    stage_data()
    stage_logs()
    with powered([GPIO.IRD, GPIO.HUB]):
        upload_staged()


if __name__ == "__main__":
    execute()
