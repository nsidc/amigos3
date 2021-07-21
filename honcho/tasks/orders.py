import os
import stat
import subprocess
from collections import namedtuple
from datetime import datetime
from logging import getLogger

from honcho.config import DATA_DIR, DATA_TAGS, FTP_ORDERS_DIR, SEP
from honcho.core.data import log_serialized
from honcho.core.ftp import ftp_session
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.common import task
from honcho.tasks.sbd import queue_sbd
from honcho.tasks.upload import queue_filepaths
from honcho.util import clear_directory

logger = getLogger(__name__)

_RESULT_KEYS = ("filename", "output", "start_time", "finish_time", "return_code")
Result = namedtuple("Result", _RESULT_KEYS)


def get_orders():
    with ftp_session() as ftp:
        ftp.cwd(FTP_ORDERS_DIR)
        orders_filenames = [el for el in ftp.nlst() if el not in (".", "..")]
        local_filepaths = []
        for filename in orders_filenames:
            logger.info("Retrieving orders: {0}".format(filename))
            local_filepath = os.path.join(DATA_DIR(DATA_TAGS.ORD), filename)
            with open(local_filepath, "w") as fo:
                ftp.retrlines("RETR " + filename, lambda line: fo.write(line + "\n"))

            local_filepaths.append(local_filepath)

    return local_filepaths


def run_script(script_filepath):
    os.chmod(script_filepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    start_time = datetime.now()
    p = subprocess.Popen(
        script_filepath, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    output, _ = p.communicate()
    finish_time = datetime.now()
    return_code = p.returncode

    return Result(
        filename=os.path.basename(script_filepath),
        output=output,
        start_time=start_time,
        finish_time=finish_time,
        return_code=return_code,
    )


def serialize(result):
    return SEP.join(
        [
            result.filename,
            result.start_time.isoformat(),
            result.finish_time.isoformat(),
            str(result.return_code),
        ]
    )


def perform_orders(orders_filepaths):
    script_filepaths = [
        filepath
        for filepath in orders_filepaths
        if filepath.endswith(".sh") or filepath.endswith(".py")
    ]
    result_filepaths = []
    for script_filepath in script_filepaths:
        script_filename = os.path.basename(script_filepath)
        logger.info("Running orders script: {0}".format(script_filename))
        result = run_script(script_filepath)

        result_filepath = os.path.join(
            DATA_DIR(DATA_TAGS.ORD), script_filename + ".out"
        )
        with open(result_filepath, "w") as fo:
            fo.write("# Start: {0}\n".format(result.start_time))
            fo.write("# Finish: {0}\n".format(result.finish_time))
            fo.write("# Return code: {0}\n".format(result.return_code))
            fo.write(result.output)

        result_filepaths.append(result_filepath)

        serialized = serialize(result)
        log_serialized(serialized, DATA_TAGS.ORD)
        queue_sbd(serialized, DATA_TAGS.ORD)

    return result_filepaths


@task
def execute():
    tag = DATA_TAGS.ORD
    clear_directory(DATA_DIR(tag))

    orders_filepaths = get_orders()
    result_filepaths = perform_orders(orders_filepaths)

    filepaths = orders_filepaths + result_filepaths
    queue_filepaths(filepaths, postfix=tag)
    archive_filepaths(result_filepaths, postfix=tag)
    clear_directory(DATA_DIR(tag))
