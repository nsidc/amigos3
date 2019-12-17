import logging
import os
from contextlib import closing, contextmanager
from datetime import datetime
from time import sleep

from serial import Serial

from honcho.config import (
    SBD_PORT,
    SBD_BAUD,
    SBD_QUEUE_DIR,
    SBD_QUEUE_ROOT_DIR,
    SBD_QUEUE_MAX_TIME,
    SBD_STARTUP_WAIT,
    GPIO,
    TIMESTAMP_FILENAME_FMT,
)
from honcho.core.gpio import powered
from honcho.core.iridium import send_sbd
from honcho.util import fail_gracefully, log_execution


logger = logging.getLogger(__name__)


@contextmanager
def sbd_components():
    with powered([GPIO.IRD, GPIO.SBD, GPIO.SER]):
        logging.debug(
            'Sleeping for {0} seconds for iridium startup'.format(SBD_STARTUP_WAIT)
        )
        sleep(SBD_STARTUP_WAIT)
        yield


def send(message):
    logging.info('Sending sbd message')
    with sbd_components():
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            send_sbd(serial, message)


def build_queue():
    queue = []
    for dirpath, _, filenames in os.walk(SBD_QUEUE_ROOT_DIR):
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


def queue_sbd(message, tag):
    logging.debug('Queuing {0} message'.format(tag))

    filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
    filepath = os.path.join(SBD_QUEUE_DIR(tag), filename)
    while os.path.exists(filepath):
        sleep(1)
        filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
        filepath = os.path.join(SBD_QUEUE_DIR(tag), filename)

    with open(filepath, 'w') as f:
        f.write(tag + ',' + message)


def clear_queue():
    logging.debug('Clearing queue')
    queue = build_queue()
    for filepath in queue:
        os.remove(filepath)


@fail_gracefully
@log_execution
def execute():
    logging.info('Sending queued sbds')
    with sbd_components():
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            send_queue(serial)


if __name__ == '__main__':
    execute()
