import re
from collections import namedtuple
from datetime import datetime
from time import sleep
from contextlib import closing

from serial import Serial

from honcho.tasks.common import task
from honcho.util import serial_request
from honcho.core.gpio import powered
from honcho.core.system import set_datetime
from honcho.config import (
    GPIO,
    GPS_PORT,
    GPS_BAUD,
    DATA_TAGS,
    GPS_STARTUP_WAIT,
    TIMESTAMP_FMT,
)
from honcho.tasks.sbd import queue_sbd
import honcho.core.data as data

_DATA_KEYS = (
    'timestamp',
    'latitude',
    'latitude_hemi',
    'longitude',
    'longitude_hemi',
    'quality',
    'sat_count',
    'hdop',
    'altitude',
    'altitude_units',
    'geoid_sep',
    'geoid_sep_units',
    'ref_id',
    'checksum',
)
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
CONVERSION_TO_VALUE = {
    DATA_KEYS.TIMESTAMP: lambda v: v,
    DATA_KEYS.LATITUDE: float,
    DATA_KEYS.LATITUDE_HEMI: str,
    DATA_KEYS.LONGITUDE: float,
    DATA_KEYS.LONGITUDE_HEMI: str,
    DATA_KEYS.QUALITY: int,
    DATA_KEYS.SAT_COUNT: int,
    DATA_KEYS.HDOP: float,
    DATA_KEYS.ALTITUDE: float,
    DATA_KEYS.ALTITUDE_UNITS: str,
    DATA_KEYS.GEOID_SEP: float,
    DATA_KEYS.GEOID_SEP_UNITS: str,
    DATA_KEYS.REF_ID: str,
    DATA_KEYS.CHECKSUM: lambda x: int(x[1:], 16),
}
CONVERSION_TO_STRING = {
    DATA_KEYS.TIMESTAMP: '{0:' + TIMESTAMP_FMT + '}',
    DATA_KEYS.LATITUDE: '{0:.2f}',
    DATA_KEYS.LATITUDE_HEMI: None,
    DATA_KEYS.LONGITUDE: '{0:.2f}',
    DATA_KEYS.LONGITUDE_HEMI: None,
    DATA_KEYS.QUALITY: '{0}',
    DATA_KEYS.SAT_COUNT: '{0}',
    DATA_KEYS.HDOP: '{0:.2f}',
    DATA_KEYS.ALTITUDE: '{0:.4f}',
    DATA_KEYS.ALTITUDE_UNITS: '{0}',
    DATA_KEYS.GEOID_SEP: '{0:.4f}',
    DATA_KEYS.GEOID_SEP_UNITS: '{0:.2f}',
    DATA_KEYS.REF_ID: '{0}',
    DATA_KEYS.CHECKSUM: '{0:02X}',
}
GGASample = namedtuple('GGASample', DATA_KEYS)


def query_gga(serial):
    expected_response = re.escape('$GPGGA') + '.*' + re.escape('\r\n')
    raw = serial_request(serial, 'out,,nmea/GGA', expected_response, timeout=10)

    return raw


def get_datetime(serial):
    expected_response = r'.*? [\d-]+' + re.escape('\r\n')
    raw_date = serial_request(
        serial, 'print,/par/time/utc/date', expected_response, timeout=10
    )

    expected_response = r'.*? [\d\.:]+' + re.escape('\r\n')
    raw_time = serial_request(
        serial, 'print,/par/time/utc/clock', expected_response, timeout=10
    )

    timestamp = datetime.strptime(
        raw_date.strip().split()[1] + ' ' + raw_time.strip().split()[1],
        '%Y-%m-%d %H:%M:%S.%f',
    )

    return timestamp


def parse_gga(raw, timestamp):
    pattern = re.escape('$GPGGA,') + '(?P<data>.*)' + re.escape('\r\n')
    data = re.search(pattern, raw).group('data').split(',')
    time = datetime.strptime(data[0], '%H%M%S.%f')
    timestamp = timestamp.replace(
        hour=time.hour, minute=time.minute, second=time.second
    )
    data = [timestamp] + data[1:]
    sample = GGASample(
        **dict(
            (key, CONVERSION_TO_VALUE[key](data[i])) for i, key in enumerate(DATA_KEYS)
        )
    )

    return sample


def get_gga():
    with powered([GPIO.SER, GPIO.GPS]):
        sleep(GPS_STARTUP_WAIT)
        with closing(Serial(GPS_PORT, GPS_BAUD)) as serial:
            timestamp = get_datetime(serial)
            set_datetime(timestamp)
            sample = parse_gga(query_gga(serial), timestamp)

    return sample


@task
def execute():
    sample = get_gga()
    serialized = data.serialize(sample, CONVERSION_TO_STRING)
    data.log_serialized(serialized, DATA_TAGS.GGA)
    queue_sbd(serialized, DATA_TAGS.GGA)
