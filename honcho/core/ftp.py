from ftplib import FTP
from contextlib import contextmanager, closing

from honcho.util import get_creds
from honcho.core.gpio import powered

from honcho.config import (
    GPIO,
    FTP_HOST,
    FTP_TIMEOUT,
)


@contextmanager
def ftp_session():
    with powered([GPIO.IRD, GPIO.HUB]):
        with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
            ftp.login(*get_creds(FTP_HOST))
            yield
