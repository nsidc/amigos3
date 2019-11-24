import logging
import os
from contextlib import closing
from datetime import datetime

from serial import Serial

from honcho.config import (
    SBD_PORT,
    SBD_BAUD,
    SBD_QUEUE_DIR,
    SBD_QUEUE_MAX_TIME,
    GPIO,
)
from honcho.core.gpio import powered
from honcho.core.iridium import send_sbd
from honcho.util import fail_gracefully, ensure_dirs


logger = logging.getLogger(__name__)


def send(message):
    logging.info('Sending sbd message')
    with powered([GPIO.IRD, GPIO.SBD, GPIO.SER]):
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            send_sbd(serial, message)


def build_queue():
    queue = []
    for dirpath, _, filenames in os.walk(SBD_QUEUE_DIR):
        queue.extend([os.path.join(dirpath, filename) for filename in filenames])

    queue = sorted(queue, key=lambda x: os.path.split(x)[-1])

    return queue


def send_queue(serial, timeout=SBD_QUEUE_MAX_TIME):
    queue = build_queue()
    for filepath in queue:
        logging.debug('Sending queued: {0}'.format(filepath))
        with open(filepath, 'r') as f:
            tag = os.path.split(filepath)[-2]
            send_sbd(serial=serial, message=tag + ',' + f.read())
            os.remove(filepath)


def queue_sbd(tag, message):
    logging.debug('Queuing {0} message'.format(tag))
    directory = os.path.join(SBD_QUEUE_DIR, tag)
    ensure_dirs([directory])
    filename = datetime.now().isoformat()
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        f.write(tag + ',' + message)


def clear_queue():
    logging.debug('Clearing queue')
    queue = build_queue()
    for filepath in queue:
        os.remove(filepath)


@fail_gracefully
def execute():
    logging.info('Sending queued sbds')
    with powered([GPIO.IRD, GPIO.SBD, GPIO.SER]):
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            send_queue(serial)


if __name__ == '__main__':
    execute()
