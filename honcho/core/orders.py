import os
import stat
import subprocess
from contextlib import closing
from datetime import datetime
from ftplib import FTP
from logging import getLogger
from netrc import netrc

from honcho.util import ensure_dirs

HOST = 'restricted_ftp'
FTP_TIMEOUT = 60
FTP_ORDERS_DIR = 'orders'
FTP_RESULTS_DIR = 'orders/results'
ORDERS_DIR = './'
# ORDERS_DIR = '/media/mmcblk0p1/orders'
RESULTS_DIR = './'
# RESULTS_DIR = '/media/mmcblk0p1/orders/results'


ensure_dirs([ORDERS_DIR, RESULTS_DIR])
logger = getLogger(__name__)


def get_creds():
    nrc = netrc()
    user, _, passwd = nrc.hosts[HOST]

    return user, passwd


def get_orders():
    with closing(FTP(HOST, timeout=FTP_TIMEOUT)) as ftp:
        ftp.login(*get_creds())
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
    orders_scripts = [el for el in os.listdir(ORDERS_DIR) if el.endswith('.sh')]
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

        result_filepath = os.path.join(RESULTS_DIR, script_filename + '.out')
        with open(result_filepath, 'w') as fo:
            fo.write('# Start: {0}\n'.format(start_time))
            fo.write('# Finish: {0}\n'.format(finish_time))
            fo.write('# Returncode: {0}\n'.format(returncode))
            fo.write(result)


def report_results():
    with closing(FTP(HOST, timeout=FTP_TIMEOUT)) as ftp:
        ftp.login(*get_creds())
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
