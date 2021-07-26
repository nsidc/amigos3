import logging
import os
from collections import namedtuple
from contextlib import closing, contextmanager
from datetime import datetime
from time import sleep

from serial import Serial

from honcho.config import (DATA_TAGS, GPIO, SBD_BAUD, SBD_PORT, SBD_QUEUE_DIR,
                           SBD_QUEUE_FILENAME, SBD_QUEUE_MAX_TIME, SBD_SIGNAL_TRIES,
                           SBD_SIGNAL_WAIT, SBD_STARTUP_WAIT)
from honcho.core.gpio import powered
from honcho.core.iridium import check_signal, send_sbd
from honcho.tasks.common import task
from honcho.tasks.upload import queue_filepaths

logger = logging.getLogger(__name__)

SBDQueueCountSample = namedtuple("SBDQueueCountSample", DATA_TAGS)


@contextmanager
def sbd_components():
    with powered([GPIO.SER, GPIO.SBD, GPIO.IRD]):
        logger.debug(
            "Sleeping for {0} seconds for iridium startup".format(SBD_STARTUP_WAIT)
        )
        sleep(SBD_STARTUP_WAIT)
        yield


def send(message):
    logger.info("Sending sbd message")
    with sbd_components():
        with closing(Serial(SBD_PORT, SBD_BAUD, timeout=60)) as serial:
            send_sbd(serial, message)


def build_queue():
    queue = [
        os.path.join(SBD_QUEUE_DIR, filename) for filename in os.listdir(SBD_QUEUE_DIR)
    ]

    # Sort by filename
    queue = sorted(queue, key=lambda x: os.path.split(x)[-1])

    return queue


def send_queue(serial, timeout=SBD_QUEUE_MAX_TIME):
    queue = build_queue()
    logger.info("Sending {0} queued sbds".format(len(queue)))
    for filepath in queue:
        logger.debug("Sending: {0}".format(filepath))
        with open(filepath, "r") as f:
            message = f.read().strip()
        try:
            assert ("\n" not in message) and ("\r" not in message)
            send_sbd(serial=serial, message=message)
        except Exception:
            queue_filepaths([filepath])
        finally:
            os.remove(filepath)


def queue_sbd(message, tag):
    logger.debug("Queuing {0} message".format(tag))

    filename = SBD_QUEUE_FILENAME(timestamp=datetime.now(), tag=tag)
    filepath = os.path.join(SBD_QUEUE_DIR, filename)
    while os.path.exists(filepath):
        sleep(1)
        filename = SBD_QUEUE_FILENAME(timestamp=datetime.now(), tag=tag)
        filepath = os.path.join(SBD_QUEUE_DIR, filename)

    with open(filepath, "w") as f:
        f.write(tag + "," + message)


def print_queue():
    print("-" * 80)
    queue = build_queue()
    for el in queue:
        print(el)


def clear_queue():
    logger.debug("Clearing queue")
    queue = build_queue()
    for filepath in queue:
        os.remove(filepath)


@task
def execute():
    queue = build_queue()
    if queue:
        with sbd_components():
            with closing(Serial(SBD_PORT, SBD_BAUD, timeout=60)) as serial:
                for _ in xrange(SBD_SIGNAL_TRIES):
                    signal = check_signal(serial)
                    if signal >= 4:
                        break
                    sleep(SBD_SIGNAL_WAIT)
                else:
                    msg = "Signal strength still too low after {0} tries, aborting"
                    raise Exception(msg.format(SBD_SIGNAL_TRIES))

                send_queue(serial)
    else:
        logger.debug("No SBD messages queued")
