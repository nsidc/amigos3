import socket
import logging
import traceback
from ftplib import FTP
from time import sleep
from contextlib import contextmanager, closing

from honcho.util import get_creds
from honcho.core.gpio import powered

from honcho.config import (
    GPIO,
    DIALOUT_WAIT,
    FTP_HOST,
    FTP_CONNECT_RETRIES,
    FTP_RETRY_WAIT,
    FTP_TIMEOUT,
)


logger = logging.getLogger(__name__)


@contextmanager
def ftp_session():
    with powered([GPIO.IRD, GPIO.RTR, GPIO.HUB]):
        logger.debug(
            'Waiting {0} seconds before attempting ftp session'.format(DIALOUT_WAIT)
        )
        sleep(DIALOUT_WAIT)
        retries = 0
        while retries <= FTP_CONNECT_RETRIES:
            try:
                with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
                    ftp.login(*get_creds(FTP_HOST))
                    yield ftp
                    break
            except socket.error:
                logger.debug(traceback.format_exc())
                logger.debug('FTP connection failed')
                if retries >= FTP_CONNECT_RETRIES:
                    raise Exception(
                        'FTP failed after {0} retries'.format(FTP_CONNECT_RETRIES)
                    )
                retries += 1
                logger.debug(
                    'Waiting {0} seconds before retrying ftp session'.format(
                        FTP_RETRY_WAIT
                    )
                )
                sleep(FTP_RETRY_WAIT)
