#!/usr/bin/env python
import os

from honcho.core.system import reboot

REBOOTED_FILE = os.path.join('/media/mmcblk0p1', 'rebooted')


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


if not os.path.exists(REBOOTED_FILE):
    touch(REBOOTED_FILE)
    reboot()
