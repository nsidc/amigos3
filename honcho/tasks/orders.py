import os
import stat
import subprocess
from collections import namedtuple
from contextlib import closing
from datetime import datetime
from logging import getLogger

from honcho.util import get_creds, log_execution, fail_gracefully
from honcho.core.gpio import powered
import honcho.tasks.sbd as sbd
from honcho.config import (
    SEP,
    GPIO,
    FTP_HOST,
    FTP_TIMEOUT,
    FTP_ORDERS_DIR,
    FTP_RESULTS_DIR,
    ORDERS_DIR,
    RESULTS_DIR,
)
from honcho.core.ftp import ftp_session


logger = getLogger(__name__)

_RESULT_KEYS = ('output', 'start_time', 'finish_time', 'return_code')
Result = namedtuple('Result', _RESULT_KEYS)


def get_orders():
    with ftp_session() as ftp:
        ftp.cwd(FTP_ORDERS_DIR)
        orders_scripts = ftp.nlst()
        for filename in orders_scripts:
            logger.info('Retrieving orders: {0}'.format(filename))
            local_script_filepath = os.path.join(ORDERS_DIR, filename)
            with open(local_script_filepath, 'w') as fo:
                ftp.retrlines('RETR ' + filename, lambda line: fo.write(line + '\n'))


def run_script(script_filepath):
    os.chmod(script_filepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    start_time = datetime.now().isoformat()
    p = subprocess.Popen(
        script_filepath, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    output, _ = p.communicate()
    finish_time = datetime.now().isoformat()
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
            result.return_code,
        ]
    )


def perform_orders():
    script_filenames = [
        el for el in os.listdir(ORDERS_DIR) if el.endswith('.sh') or el.endswith('.py')
    ]
    for script_filename in script_filenames:
        script_filepath = os.path.join(os.path.abspath(ORDERS_DIR), script_filename)
        logger.info('Runnig order script: {0}'.format(script_filename))
        result = run_script(script_filepath)

        result_filepath = os.path.join(RESULTS_DIR, script_filename + '.out')
        with open(result_filepath, 'w') as fo:
            fo.write('# Start: {0}\n'.format(result.start_time))
            fo.write('# Finish: {0}\n'.format(result.finish_time))
            fo.write('# Return code: {0}\n'.format(result.return_code))
            fo.write(result.output)

        sbd.send(serialize(result))


def report_results():
    with ftp_session() as ftp:
        ftp.cwd(FTP_RESULTS_DIR)
        results_filenames = [
            el for el in os.listdir(RESULTS_DIR) if el.endswith('.out')
        ]
        for result_filename in results_filenames:
            result_filepath = os.path.abspath(
                os.path.join(RESULTS_DIR, result_filename)
            )
            with open(result_filepath, 'r') as fi:
                ftp.storlines('STOR {}'.format(result_filename), fi)


def clean_up():
    orders_filepaths = [os.path.join(ORDERS_DIR, el) for el in os.listdir(ORDERS_DIR)]
    results_filepaths = [
        os.path.join(RESULTS_DIR, el) for el in os.listdir(RESULTS_DIR)
    ]

    for filepath in orders_filepaths + results_filepaths:
        os.remove(filepath)


@fail_gracefully
@log_execution
def execute():
    get_orders()
    perform_orders()
    report_results()
    clean_up()
