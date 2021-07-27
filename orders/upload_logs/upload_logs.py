#!/usr/bin/env python
import glob
from datetime import datetime

from honcho.tasks.upload import queue_filepaths_chunked
from honcho.config import LOGS_DIR, ARCHIVE_DIR

DATE = datetime(2020, 11, 06)


if __name__ == "__main__":
    filepaths = glob.glob(ARCHIVE_DIR + "/" + DATE.strftime("%Y_%m_%d*LOG*"))
    filepaths += glob.glob(LOGS_DIR + "/" + "honcho.tasks*")
    print("Putting chunked log files on upload queue:", filepaths)
    queue_filepaths_chunked(filepaths, prefix=DATE.strftime("%Y%m%d_logs"))
