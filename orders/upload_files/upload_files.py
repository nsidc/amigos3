#!/usr/bin/env python
import shutil

from honcho.config import UPLOAD_QUEUE_DIR

FILEPATHS = [
    '/media/mmcblk0p1/honcho/tasks/config.py',
    '/media/mmcblk0p1/honcho/tasks/config_override.py'
]

if __name__ == "__main__":
    for filepath in FILEPATHS:
        shutil.copy(filepath, UPLOAD_QUEUE_DIR)
