import os
import shutil
from datetime import datetime
from logging import getLogger

from honcho.config import UPLOAD_CLEANUP, UPLOAD_QUEUE_DIR
from honcho.core.data import chunk_file, compute_checksum, make_chunk_joiner
from honcho.core.ftp import ftp_session
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.common import task
from honcho.util import clear_directory, file_size

logger = getLogger(__name__)


def queue_filepaths(filepaths, prefix=None, postfix=None, tarball=True):
    queued_filepaths = []
    if tarball:
        queued_filepaths.append(
            archive_filepaths(
                filepaths, prefix, postfix, output_directory=UPLOAD_QUEUE_DIR
            )
        )
    else:
        for filepath in filepaths:
            queued_filepath = os.path.join(UPLOAD_QUEUE_DIR, os.path.basename(filepath))
            shutil.copy(filepath, queued_filepath)
            queued_filepaths.append(queued_filepath)

    return queued_filepaths


def queue_filepaths_chunked(filepaths, prefix=None, postfix=None):
    tarball_filepath = archive_filepaths(
        filepaths, prefix, postfix, output_directory=UPLOAD_QUEUE_DIR
    )
    checksum = compute_checksum(tarball_filepath)
    chunk_filepaths = chunk_file(tarball_filepath, UPLOAD_QUEUE_DIR)
    joiner_filepath = make_chunk_joiner(chunk_filepaths, checksum)

    os.remove(tarball_filepath)

    return chunk_filepaths + [joiner_filepath]


def upload(filepath, session):
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as fi:
        logger.debug("Uploading {0} bytes: {1}".format(file_size(filepath), filepath))
        start = datetime.now()
        session.storbinary("STOR {0}".format(filename), fi)
        logger.debug("Upload successful: {0}".format(datetime.now() - start))


def print_queue():
    for filename in os.listdir(UPLOAD_QUEUE_DIR):
        filepath = os.path.join(UPLOAD_QUEUE_DIR, filename)
        print("\t".join([file_size(filepath), filepath]))


def clear_queue():
    clear_directory(UPLOAD_QUEUE_DIR)


@task
def execute():
    filenames = os.listdir(UPLOAD_QUEUE_DIR)
    if not filenames:
        logger.debug("No files queued for upload")
        return
    with ftp_session() as session:
        logger.debug("Queued files for upload: {0}".format(len(filenames)))
        for filename in filenames:
            filepath = os.path.join(UPLOAD_QUEUE_DIR, filename)
            upload(filepath, session=session)

            if UPLOAD_CLEANUP:
                os.remove(filepath)
