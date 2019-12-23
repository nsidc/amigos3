import os
import logging
from time import sleep
from datetime import datetime, timedelta
from contextlib import closing

from serial import Serial

from honcho.core.gpio import powered
from honcho.tasks.upload import stage_path
from honcho.tasks.common import task
from honcho.config import (
    DATA_TAGS,
    DATA_LOG_FILENAME,
    DATA_DIR,
    GPS_PORT,
    GPS_BAUD,
    GPS_STARTUP_WAIT,
    GPIO,
    SECONDS_PER_MEASUREMENT,
    MEASUREMENTS,
)

logger = logging.getLogger(__name__)


def query_tps(serial, output_filepath):
    start_sequence = [
        'set,/par/ant/rcv/inp,ext\r\n',
        'dm\r\n',
        'dm,,/msg/jps/D1\r\n',
        'dm,,/msg/jps/D2\r\n',
        'set,lock/glo/fcn,n\r\n',
        'em,,def:{0:.2f}&&em,,jps/ET:{0:.2f}\r\n'.format(SECONDS_PER_MEASUREMENT),
    ]
    start_command = 'em,,def:{0:.2f}&&em,,jps/ET:{0:.2f}\r\n'.format(
        SECONDS_PER_MEASUREMENT
    )

    stop_command = 'dm'

    logger.debug('Sending TPS setup command sequence')
    for cmd in start_sequence:
        sleep(2)
        serial.write(cmd)

    logger.debug('Starting TPS stream')
    serial.write(start_command)
    end_time = datetime.now() + MEASUREMENTS * timedelta(
        seconds=SECONDS_PER_MEASUREMENT
    )
    with open(output_filepath, 'wb') as f:
        data = ''
        while datetime.now() < end_time or data:
            sleep(5)
            data = serial.read(serial.inWaiting())
            logger.debug('Read {0} bytes from tps stream'.format(len(data)))
            f.write(data)

    logger.debug('Stopping TPS stream')
    serial.write(stop_command)


def get_tps():
    filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + '.tps'
    output_filepath = os.path.join(DATA_DIR(DATA_TAGS.TPS), filename)
    with powered([GPIO.SER, GPIO.GPS]):
        sleep(GPS_STARTUP_WAIT)
        with closing(Serial(GPS_PORT, GPS_BAUD)) as serial:
            query_tps(serial, output_filepath)


@task
def execute():
    get_tps()
    stage_path(DATA_DIR(DATA_TAGS.BNX))
