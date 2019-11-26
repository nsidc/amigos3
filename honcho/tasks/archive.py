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
    clear_directory,
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


def get_session(retries=FTP_CONNECT_RETRIES):
    logger.debug('Attempting to connect to {0}'.format(FTP_HOST))
    for attempt in xrange(1, retries + 2):
        try:
            session = FTP(FTP_HOST, timeout=FTP_TIMEOUT)
            session.login(*get_creds(FTP_HOST))
        except Exception:
            logger.debug('Connection failed {0}/{1}'.format(attempt, retries + 1))
            retries -= 1
        else:
            break

    logger.debug('Session initiated on {0} attempt')

    return session


def upload(filepath, session=None):
    if session is None:
        session = get_session()

    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as fi:
        logger.debug('Uploading {0} bytes: {1}'.format(file_size(filepath), filepath))
        session.storbinary('STOR {0}'.format(filename), fi)
        logger.debug('Upload successful')


def archive_data():
    for tag in DATA_TAGS:
        path = os.path.join(DATA_DIR, tag)
        name = tag + '_' + serialize_datetime(datetime.now()) + '.tgz'
        output_filepath = os.path.join(DATASTORE_DIR, name)
        make_tarfile(output_filepath, path)


def archive_logs():
    name = 'LOG_' + serialize_datetime(datetime.now()) + '.tgz'
    output_filepath = os.path.join(DATASTORE_DIR, name)
    make_tarfile(output_filepath, LOG_DIR)


def archive():
    logger.debug('Archiving data')
    archive_data()
    archive_logs()

    logger.debug('Cleaning up')
    clear_directory(DATA_DIR)


@fail_gracefully
def execute():
    ensure_dirs([STAGED_UPLOAD_DIR])
    staged_data_files = stage_data()
    staged_log_files = stage_logs()
    try:
        with powered([GPIO.IRD, GPIO.HUB]):
            with closing(get_session()) as session:
                for filepath in staged_data_files + staged_log_files:
                    upload(filepath, session=session)

                    if UPLOAD_CLEANUP:
                        os.remove(filepath)
    finally:
        archive()


if __name__ == "__main__":
    execute()
