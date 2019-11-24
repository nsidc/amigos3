import os
from ftplib import FTP
from logging import getLogger
from contextlib import closing

from honcho.config import STAGED_UPLOAD_DIR, FTP_HOST, FTP_TIMEOUT
from honcho.util import get_creds, ensure_dirs, fail_gracefully
from honcho.core.gpio import powered


logger = getLogger(__name__)


@fail_gracefully
def execute():
    ensure_dirs([STAGED_UPLOAD_DIR])
    with powered(['ird', 'hub']):
        with closing(FTP(FTP_HOST, timeout=FTP_TIMEOUT)) as ftp:
            ftp.login(*get_creds(FTP_HOST))
            filenames = os.listdir(STAGED_UPLOAD_DIR)
            for filename in filenames:
                filepath = os.path.join(STAGED_UPLOAD_DIR, filename)
                with open(filepath, 'rb') as fi:
                    ftp.storbinary('STOR {}'.format(filename), fi)


if __name__ == "__main__":
    execute()
