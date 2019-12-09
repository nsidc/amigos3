import time
from datetime import datetime
from contextlib import closing
from collections import namedtuple

from serial import Serial

from honcho.util import fail_gracefully, log_execution, serialize_datetime
from honcho.config import WXT_PORT, WXT_BAUD, WXT_SAMPLES, DATA_TAGS, SEP, GPIO
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_data
from honcho.core.gpio import powered

_DATA_KEYS = (
    'TIMESTAMP',
    'WIND_DIRECTION',
    'WIND_SPEED',
    'TEMPERATURE',
    'HUMIDITY',
    'PRESSURE',
    'RAIN_ACCUMULATION',
    'RAIN_DURATION',
    'RAIN_INTENSITY',
    'RAIN_PEAK_INTENSITY',
    'HAIL_ACCUMULATION',
    'HAIL_DURATION',
    'HAIL_INTENSITY',
    'HAIL_PEAK_INTENSITY',
    'HEATER_TEMPERATURE',
    'HEATER_VOLTAGE',
    'SUPPLY_VOLTAGE',
)
_VALUE_KEYS = _DATA_KEYS[1:]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
VALUE_KEYS = namedtuple('VALUE_KEYS', _VALUE_KEYS)(*_VALUE_KEYS)
VALUE_CONVERSIONS = {
    VALUE_KEYS.WIND_DIRECTION: float,
    VALUE_KEYS.WIND_SPEED: float,
    VALUE_KEYS.TEMPERATURE: float,
    VALUE_KEYS.HUMIDITY: float,
    VALUE_KEYS.PRESSURE: float,
    VALUE_KEYS.RAIN_ACCUMULATION: float,
    VALUE_KEYS.RAIN_DURATION: float,
    VALUE_KEYS.RAIN_INTENSITY: float,
    VALUE_KEYS.RAIN_PEAK_INTENSITY: float,
    VALUE_KEYS.HAIL_ACCUMULATION: float,
    VALUE_KEYS.HAIL_DURATION: float,
    VALUE_KEYS.HAIL_INTENSITY: float,
    VALUE_KEYS.HAIL_PEAK_INTENSITY: float,
    VALUE_KEYS.HEATER_TEMPERATURE: float,
    VALUE_KEYS.HEATER_VOLTAGE: float,
    VALUE_KEYS.SUPPLY_VOLTAGE: float,
}
STRING_CONVERSIONS = {
    VALUE_KEYS.WIND_DIRECTION: '{0:.4f}',
    VALUE_KEYS.WIND_SPEED: '{0:.4f}',
    VALUE_KEYS.TEMPERATURE: '{0:.4f}',
    VALUE_KEYS.HUMIDITY: '{0:.4f}',
    VALUE_KEYS.PRESSURE: '{0:.4f}',
    VALUE_KEYS.RAIN_ACCUMULATION: '{0:.4f}',
    VALUE_KEYS.RAIN_DURATION: '{0:.4f}',
    VALUE_KEYS.RAIN_INTENSITY: '{0:.4f}',
    VALUE_KEYS.RAIN_PEAK_INTENSITY: '{0:.4f}',
    VALUE_KEYS.HAIL_ACCUMULATION: '{0:.4f}',
    VALUE_KEYS.HAIL_DURATION: '{0:.4f}',
    VALUE_KEYS.HAIL_INTENSITY: '{0:.4f}',
    VALUE_KEYS.HAIL_PEAK_INTENSITY: '{0:.4f}',
    VALUE_KEYS.HEATER_TEMPERATURE: '{0:.4f}',
    VALUE_KEYS.HEATER_VOLTAGE: '{0:.4f}',
    VALUE_KEYS.SUPPLY_VOLTAGE: '{0:.4f}',
}
SAMPLE = namedtuple('SAMPLE', DATA_KEYS)


def parse_sample(s):
    row = s.split()
    sample = SAMPLE(
        TIMESTAMP=datetime.strptime(' '.join(row[4:-1]), '%d %b %Y %H:%M:%S'),
        **dict(
            (key, VALUE_CONVERSIONS[key](row[i])) for i, key in enumerate(VALUE_KEYS)
        )
    )

    return sample


def get_samples(n=12):
    samples = []
    with powered([GPIO.WXT, GPIO.SER]):
        with closing(Serial(WXT_PORT, WXT_BAUD)) as serial:
            while len(samples) < 12:
                samples.append(parse_sample(serial.readline()))

    return samples


def average_samples(samples):
    n = len(samples)
    timestamp = datetime.fromtimestamp(
        sum(time.mktime(sample.TIMESTAMP.timetuple()) for sample in samples) / n
    )
    averaged = SAMPLE(
        timestamp=timestamp,
        **dict(
            (key, sum(getattr(sample, key) for sample in samples) / float(n))
            for key in VALUE_KEYS
        )
    )

    return averaged


def print_samples(samples):
    print(', '.join(DATA_KEYS))
    print('-' * 80)
    for sample in samples:
        print(serialize(sample).replace(SEP, ', '))


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.TIMESTAMP)]
        + [STRING_CONVERSIONS[key].format(getattr(sample, key)) for key in VALUE_KEYS]
    )

    return serialized


@fail_gracefully
@log_execution
def execute():
    samples = get_samples(n=WXT_SAMPLES)
    average = average_samples(samples)
    serialized = serialize(average)
    log_data(serialized, DATA_TAGS.WXT)
    queue_sbd(DATA_TAGS.WXT, serialized)


if __name__ == '__main__':
    execute()
