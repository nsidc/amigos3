import shutil
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
    DATA_DIR,
    DATA_TAGS,
    STAGED_UPLOAD_DIR,
    UPLOAD_DATA_TAGS,
    UPLOAD_CLEANUP,
    DATASTORE_DIR,
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

    return output_filepath


def stage_data():
    staged = []
    for i, tag in enumerate(UPLOAD_DATA_TAGS):
        staged.append(stage_path(os.path.join(DATA_DIR, tag), i))

    return staged


def stage_logs():
    staged = []
    for logfile in os.listdir(LOG_DIR):
        staged.append(stage_path(os.path.join(LOG_DIR, logfile)))

    return staged


def upload(filepaths):
    with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
        ftp.login(*get_creds(FTP_HOST))
        logger.debug('Logged in to {0}'.format(FTP_HOST))
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as fi:
                logger.debug(
                    'Uploading {0} bytes: {1}'.format(file_size(filepath), filepath)
                )
                ftp.storbinary('STOR {0}'.format(filename), fi)
                logger.debug('Upload successful')


def store_data_dir():
    for tag in DATA_TAGS:
        path = os.path.join(DATA_DIR, tag)
        name = tag + '_' + serialize_datetime(datetime.now()) + '.tgz'
        output_filepath = os.path.join(DATASTORE_DIR, name)
        make_tarfile(output_filepath, path)


def store_log():
    name = 'LOG_' + serialize_datetime(datetime.now()) + '.tgz'
    output_filepath = os.path.join(DATASTORE_DIR, name)
    make_tarfile(output_filepath, LOG_DIR)


@fail_gracefully
def execute():
    ensure_dirs([STAGED_UPLOAD_DIR])
    staged_data_files = stage_data()
    staged_logs_files = stage_logs()
    try:
        with powered([GPIO.IRD, GPIO.HUB]):
            upload(staged_data_files + staged_logs_files)
    except Exception:
        logger.error('Errors raised during upload')
        raise
    finally:
        logger.info('Rotating data to storage')
        store_data_dir()
        store_log()
        shutil.rmtree(STAGED_UPLOAD_DIR)
        shutil.rmtree(DATA_DIR)


if __name__ == "__main__":
    execute()
