import logging
import os
from collections import namedtuple
from contextlib import closing, contextmanager
from datetime import datetime
from time import sleep

from serial import Serial

from honcho.config import (
    DATA_TAGS,
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
from honcho.tasks.common import task


logger = logging.getLogger(__name__)

SBDQueueCountSample = namedtuple('SBDQueueCountSample', DATA_TAGS)


@contextmanager
def sbd_components():
    with powered([GPIO.IRD, GPIO.SBD, GPIO.SER]):
        logger.debug(
            'Sleeping for {0} seconds for iridium startup'.format(SBD_STARTUP_WAIT)
        )
        sleep(SBD_STARTUP_WAIT)
        yield


def send(message):
    logger.info('Sending sbd message')
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
        logger.debug('Sending queued: {0}'.format(filepath))
        with open(filepath, 'r') as f:
            tag = os.path.split(filepath)[-2]
            send_sbd(serial=serial, message=tag + ',' + f.read())

        os.remove(filepath)


def queue_sbd(message, tag):
    logger.debug('Queuing {0} message'.format(tag))

    filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
    filepath = os.path.join(SBD_QUEUE_DIR(tag), filename)
    while os.path.exists(filepath):
        sleep(1)
        filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT)
        filepath = os.path.join(SBD_QUEUE_DIR(tag), filename)

    with open(filepath, 'w') as f:
        f.write(tag + ',' + message)


def print_queue():
    counts = get_queue_counts()
    print(
        '\n'.join(
            '{0}: {1}'.format(name, count)
            for name, count in zip(SBDQueueCountSample._fields, counts)
        )
    )
    print('-' * 80)
    queue = build_queue()
    for el in queue:
        print(el)


def get_queue_counts():
    return SBDQueueCountSample(
        **dict((tag, len(os.listdir(SBD_QUEUE_DIR(tag)))) for tag in DATA_TAGS)
    )


def clear_queue():
    logger.debug('Clearing queue')
    queue = build_queue()
    for filepath in queue:
        os.remove(filepath)


@task
def execute():
    logger.info('Sending queued sbds')
    with sbd_components():
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            send_queue(serial)
