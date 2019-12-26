import os
from logging import getLogger
from collections import namedtuple

from honcho.config import UPLOAD_QUEUE_DIR, UPLOAD_CLEANUP
from honcho.util import file_size, clear_directory
from honcho.tasks.common import task
from honcho.tasks.archive import archive_filepaths
from honcho.core.ftp import ftp_session

logger = getLogger(__name__)

UploadQueueCountSample = namedtuple('UploadQueueCountSample', 'files')


def queue_filepaths(filepaths, prefix):
    archive_filepaths(filepaths, prefix, output_directory=UPLOAD_QUEUE_DIR)


def upload(filepath, session):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as fi:
        logger.debug('Uploading {0} bytes: {1}'.format(file_size(filepath), filepath))
        session.storbinary('STOR {0}'.format(filename), fi)
        logger.debug('Upload successful')


def print_queue():
    for filename in os.listdir(UPLOAD_QUEUE_DIR):
        filepath = os.path.join(UPLOAD_QUEUE_DIR, filename)
        print('\t'.join([file_size(filepath), filepath]))


def clear_queue():
    clear_directory(UPLOAD_QUEUE_DIR)


def get_upload_queue_count():
    return UploadQueueCountSample(os.listdir(UPLOAD_QUEUE_DIR))


@task
def execute():
    with ftp_session() as session:
        for filename in os.listdir(UPLOAD_QUEUE_DIR):
            filepath = os.path.join(UPLOAD_QUEUE_DIR, filename)
            upload(filepath, session=session)

            if UPLOAD_CLEANUP:
                os.remove(filepath)
