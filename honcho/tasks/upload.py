import os
from logging import getLogger
from datetime import datetime

from honcho.config import (
    LOG_DIR,
    DATA_DIR,
    UPLOAD_QUEUE_DIR,
    UPLOAD_DATA_TAGS,
    UPLOAD_CLEANUP,
    TIMESTAMP_FILENAME_FMT,
)
from honcho.util import file_size, make_tarfile
from honcho.tasks.common import task
from honcho.core.ftp import ftp_session

logger = getLogger(__name__)


def stage_path(path, prefix=None):
    if os.listdir(path):
        logger.debug('Staging {0}'.format(path))
        name = (
            os.path.basename(path)
            + '_'
            + datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
            + '.tgz'
        )
        if prefix is not None:
            name = '{0}_{1}'.format(prefix, name)
        output_filepath = os.path.join(UPLOAD_QUEUE_DIR, name)
        make_tarfile(output_filepath, path)

        return output_filepath
    else:
        logger.debug('Nothing in {0} to stage'.format(path))


def stage_logs():
    staged = []
    for logfile in os.listdir(LOG_DIR):
        staged.append(stage_path(os.path.join(LOG_DIR, logfile)))

    return staged


def upload(filepath, session):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as fi:
        logger.debug('Uploading {0} bytes: {1}'.format(file_size(filepath), filepath))
        session.storbinary('STOR {0}'.format(filename), fi)
        logger.debug('Upload successful')


@task
def execute():
    staged_log_files = stage_logs()
    with ftp_session() as session:
        for filepath in staged_data_files + staged_log_files:
            upload(filepath, session=session)

            if UPLOAD_CLEANUP:
                os.remove(filepath)
