import re
import subprocess
from collections import namedtuple
from datetime import datetime
from time import sleep
from contextlib import closing

from serial import Serial

from honcho.util import fail_gracefully, log_execution, serialize_datetime
from honcho.util import serial_request
from honcho.core.gpio import powered
from honcho.config import GPIO, GPS_PORT, GPS_BAUD, DATA_TAGS, SEP, GPS_STARTUP_WAIT
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_data

_DATA_KEYS = (
    'TIMESTAMP',
    'LATITUDE',
    'LATITUDE_HEMI',
    'LONGITUDE',
    'LONGITUDE_HEMI',
    'QUALITY',
    'SAT_COUNT',
    'HDOP',
    'ALTITUDE',
    'ALTITUDE_UNITS',
    'GEOID_SEP',
    'GEOID_SEP_UNITS',
    'AGE',
    'REF_ID',
    'CHECKSUM',
)
_VALUE_KEYS = _DATA_KEYS[1:]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
VALUE_KEYS = namedtuple('VALUE_KEYS', _VALUE_KEYS)(*_VALUE_KEYS)
VALUE_CONVERSIONS = {
    VALUE_KEYS.LATITUDE: float,
    VALUE_KEYS.LATITUDE_HEMI: str,
    VALUE_KEYS.LONGITUDE: float,
    VALUE_KEYS.LONGITUDE_HEMI: str,
    VALUE_KEYS.QUALITY: int,
    VALUE_KEYS.SAT_COUNT: int,
    VALUE_KEYS.HDOP: float,
    VALUE_KEYS.ALTITUDE: float,
    VALUE_KEYS.ALTITUDE_UNITS: str,
    VALUE_KEYS.GEOID_SEP: float,
    VALUE_KEYS.GEOID_SEP_UNITS: str,
    VALUE_KEYS.AGE: float,
    VALUE_KEYS.REF_ID: str,
    VALUE_KEYS.CHECKSUM: lambda x: int(x, 16),
}
STRING_CONVERSIONS = {
    VALUE_KEYS.LATITUDE: '{0:.2f}',
    VALUE_KEYS.LATITUDE_HEMI: '{0}',
    VALUE_KEYS.LONGITUDE: '{0:.2f}',
    VALUE_KEYS.LONGITUDE_HEMI: '{0}',
    VALUE_KEYS.QUALITY: '{0}',
    VALUE_KEYS.SAT_COUNT: '{0}',
    VALUE_KEYS.HDOP: '{0:.2f}',
    VALUE_KEYS.ALTITUDE: '{0:.4f}',
    VALUE_KEYS.ALTITUDE_UNITS: '{0}',
    VALUE_KEYS.GEOID_SEP: '{0:.4f}',
    VALUE_KEYS.GEOID_SEP_UNITS: '{0:.2f}',
    VALUE_KEYS.AGE: '{0:.1f}',
    VALUE_KEYS.REF_ID: '{0}',
    VALUE_KEYS.CHECKSUM: '{0:02X}',
}
SAMPLE = namedtuple('SAMPLE', DATA_KEYS)


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

    sample = SAMPLE(
        timestamp=timestamp,
        **dict(
            (key, VALUE_CONVERSIONS[key](data[1:])) for i, key in enumerate(VALUE_KEYS)
        )
    )

    return sample


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.TIMESTAMP), sample.DEVICE_ID]
        + [STRING_CONVERSIONS[key].format(getattr(sample, key)) for key in VALUE_KEYS]
    )

    return serialized


def set_datetime(timestamp):
    subprocess.check_call(['date', '-s', timestamp.strftime('%Y-%m-%d %H:%M:%S')])


def get_gga():
    with powered([GPIO.SER, GPIO.GPS]):
        sleep(GPS_STARTUP_WAIT)
        with closing(Serial(GPS_PORT, GPS_BAUD)) as serial:
            timestamp = get_datetime(serial)
            set_datetime(timestamp)
            sample = parse_gga(query_gga(serial), timestamp)

    return sample


def print_samples(samples):
    print(', '.join(DATA_KEYS))
    print('-' * 80)
    for sample in samples:
        print(serialize(sample).replace(SEP, ', '))


@fail_gracefully
@log_execution
def execute():
    sample = get_gga()
    serialized = serialize(sample)
    log_data(serialized, DATA_TAGS.GGA)
    queue_sbd(DATA_TAGS.GGA, serialized)


if __name__ == '__main__':
    execute()
