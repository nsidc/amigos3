#!/usr/bin/env python
from datetime import datetime

from honcho.tasks.upload import queue_filepaths_chunked

FILEPATHS = [
    '/media/mmcblk0p1/archive/2021_05_08_18_02_00_WEST_low.jpg'
]


if __name__ == "__main__":
    print("Putting chunked log files on upload queue:", FILEPATHS)
    queue_filepaths_chunked(FILEPATHS,
                            prefix=datetime.now().strftime("%Y%m%d_large_upload"))
