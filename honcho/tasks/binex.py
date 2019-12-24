import os
import logging
from time import sleep
from datetime import datetime, timedelta
from contextlib import closing

from serial import Serial

from honcho.core.gpio import powered
from honcho.tasks.upload import queue_filepaths
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.common import task
from honcho.config import (
    DATA_TAGS,
    DATA_LOG_FILENAME,
    DATA_DIR,
    GPS_PORT,
    GPS_BAUD,
    GPIO,
)

logger = logging.getLogger(__name__)

SECONDS_PER_MEASUREMENT = 30
MEASUREMENTS = 4


def query_binex(
    serial, output_filepath, n=MEASUREMENTS, interval=SECONDS_PER_MEASUREMENT
):
    binex_cmd = (
        'out,,binex/'
        '{00_00,01_01,01_02,01_05,01_06,7E_00,7D_00,7F_02,7F_03,7F_04,7F_05}\r\n'
    )
    count = 0
    with open(output_filepath, 'wb') as f:
        next_query = datetime.now()
        while count < MEASUREMENTS:
            wait_time = next_query - datetime.now()
            if wait_time > timedelta(seconds=0):
                sleep(wait_time.seconds)

            logger.debug('Requesting binex')
            last_query = datetime.now()
            next_query = last_query + timedelta(seconds=SECONDS_PER_MEASUREMENT)
            serial.write(binex_cmd)
            length = 0
            while True:
                sleep(5)
                data = serial.read(serial.inWaiting())
                length += len(data)
                if data:
                    f.write(data)
                else:
                    logger.debug('Recieved {0} bytes for binex message'.format(length))
                    break
            count += 1


def get_binex():
    output_filepath = os.path.join(
        DATA_DIR(DATA_TAGS.BNX), DATA_LOG_FILENAME(DATA_TAGS.BNX)
    )
    with powered([GPIO.SER, GPIO.GPS]):
        with closing(Serial(GPS_PORT, GPS_BAUD)) as serial:
            query_binex(serial, output_filepath)

    return output_filepath


@task
def execute():
    filepath = get_binex()
    tag = DATA_TAGS.BNX
    queue_filepaths([filepath], prefix=tag)
    archive_filepaths([filepath], prefix=tag)
