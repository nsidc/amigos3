import os
import stat
import subprocess
from collections import namedtuple
from datetime import datetime
from logging import getLogger

from honcho.tasks.common import task
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_serialized
from honcho.config import SEP, DATA_DIR, DATA_TAGS, FTP_ORDERS_DIR, ORDERS_DIR
from honcho.core.ftp import ftp_session


logger = getLogger(__name__)

_RESULT_KEYS = ('filename', 'output', 'start_time', 'finish_time', 'return_code')
Result = namedtuple('Result', _RESULT_KEYS)


def get_orders():
    with ftp_session() as ftp:
        ftp.cwd(FTP_ORDERS_DIR)
        orders_scripts = [el for el in ftp.nlst() if el not in ('.', '..')]
        for filename in orders_scripts:
            logger.info('Retrieving orders: {0}'.format(filename))
            local_script_filepath = os.path.join(ORDERS_DIR, filename)
            with open(local_script_filepath, 'w') as fo:
                ftp.retrlines('RETR ' + filename, lambda line: fo.write(line + '\n'))


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
            'ORD',
            result.filename,
            result.start_time.isoformat(),
            result.finish_time.isoformat(),
            str(result.return_code),
        ]
    )


def perform_orders():
    script_filenames = [
        el for el in os.listdir(ORDERS_DIR) if el.endswith('.sh') or el.endswith('.py')
    ]
    for script_filename in script_filenames:
        script_filepath = os.path.join(os.path.abspath(ORDERS_DIR), script_filename)
        logger.info('Running orders script: {0}'.format(script_filename))
        result = run_script(script_filepath)

        result_filepath = os.path.join(
            DATA_DIR(DATA_TAGS.ORD), script_filename + '.out'
        )
        with open(result_filepath, 'w') as fo:
            fo.write('# Start: {0}\n'.format(result.start_time))
            fo.write('# Finish: {0}\n'.format(result.finish_time))
            fo.write('# Return code: {0}\n'.format(result.return_code))
            fo.write(result.output)

        serialized = serialize(result)
        log_serialized(serialized, DATA_TAGS.ORD)
        queue_sbd(serialize(result), DATA_TAGS.ORD)


def cleanup():
    orders_filepaths = [os.path.join(ORDERS_DIR, el) for el in os.listdir(ORDERS_DIR)]

    for filepath in orders_filepaths:
        logger.info('Cleaning up: {0}'.format(filepath))
        os.remove(filepath)


@task
def execute():
    get_orders()
    perform_orders()
    cleanup()
