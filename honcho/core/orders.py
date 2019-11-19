import os
import stat
import subprocess
from contextlib import closing
from datetime import datetime
from ftplib import FTP
from logging import getLogger

from honcho.util import ensure_dirs, get_creds
from honcho.core.gpio import powered
from honcho.config import (
    FTP_HOST,
    FTP_TIMEOUT,
    FTP_ORDERS_DIR,
    FTP_RESULTS_DIR,
    ORDERS_DIR,
    RESULTS_DIR,
)


logger = getLogger(__name__)


def get_orders():
    with powered('iridium'), powered('hub'):
        with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
            ftp.login(*get_creds(FTP_HOST))
            ftp.cwd(FTP_ORDERS_DIR)
            orders_scripts = [el for el in ftp.nlst() if el.endswith('.sh')]
            for script_filename in orders_scripts:
                logger.info('Retrieving orders: {0}'.format(script_filename))
                local_script_filepath = os.path.join(ORDERS_DIR, script_filename)
                with open(local_script_filepath, 'w') as fo:
                    ftp.retrlines(
                        'RETR ' + script_filename, lambda line: fo.write(line + '\n')
                    )


def perform_orders():
    import honcho.core.sbd as sbd

    orders_scripts = [el for el in os.listdir(ORDERS_DIR) if el.endswith('.sh')]
    overall_start_time = datetime.now().isoformat()
    errors = False
    for script_filename in orders_scripts:
        logger.info('Performing orders: {0}'.format(script_filename))
        script_filepath = os.path.join(os.path.abspath(ORDERS_DIR), script_filename)
        os.chmod(script_filepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        start_time = datetime.now().isoformat()
        p = subprocess.Popen(
            script_filepath,
            shell=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
        )
        result, _ = p.communicate()
        finish_time = datetime.now().isoformat()
        returncode = p.returncode
        errors |= returncode

        result_filepath = os.path.join(RESULTS_DIR, script_filename + '.out')
        with open(result_filepath, 'w') as fo:
            fo.write('# Start: {0}\n'.format(start_time))
            fo.write('# Finish: {0}\n'.format(finish_time))
            fo.write('# Returncode: {0}\n'.format(returncode))
            fo.write(result)

    overall_end_time = datetime.now().isoformat()
    sbd.send_message(
        'ORD, {0}, {1}, {2}, {3}'.format(
            orders_scripts, overall_start_time, overall_end_time, bool(errors)
        )
    )


def report_results():
    with powered('iridium'):
        with powered('hub'):
            with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
                ftp.login(*get_creds(FTP_HOST))
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


def execute():
    ensure_dirs([ORDERS_DIR, RESULTS_DIR])
    get_orders()
    perform_orders()
    report_results()
    clean_up()
