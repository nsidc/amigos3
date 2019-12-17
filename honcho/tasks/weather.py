import time
from datetime import datetime
from contextlib import closing
from collections import namedtuple

from serial import Serial

from honcho.util import fail_gracefully, log_execution, average_datetimes
from honcho.config import (
    WXT_PORT,
    WXT_BAUD,
    WXT_SAMPLES,
    DATA_TAGS,
    GPIO,
    TIMESTAMP_FMT,
)
from honcho.tasks.sbd import queue_sbd
import honcho.core.data as data
from honcho.core.gpio import powered

_DATA_KEYS = (
    'timestamp',
    'wind_direction',
    'wind_speed',
    'temperature',
    'humidity',
    'pressure',
    'rain_accumulation',
    'rain_duration',
    'rain_intensity',
    'rain_peak_intensity',
    'hail_accumulation',
    'hail_duration',
    'hail_intensity',
    'hail_peak_intensity',
    'heater_temperature',
    'heater_voltage',
    'supply_voltage',
)
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
CONVERSION_TO_VALUE = {
    DATA_KEYS.WIND_DIRECTION: float,
    DATA_KEYS.WIND_SPEED: float,
    DATA_KEYS.TEMPERATURE: float,
    DATA_KEYS.HUMIDITY: float,
    DATA_KEYS.PRESSURE: float,
    DATA_KEYS.RAIN_ACCUMULATION: float,
    DATA_KEYS.RAIN_DURATION: float,
    DATA_KEYS.RAIN_INTENSITY: float,
    DATA_KEYS.RAIN_PEAK_INTENSITY: float,
    DATA_KEYS.HAIL_ACCUMULATION: float,
    DATA_KEYS.HAIL_DURATION: float,
    DATA_KEYS.HAIL_INTENSITY: float,
    DATA_KEYS.HAIL_PEAK_INTENSITY: float,
    DATA_KEYS.HEATER_TEMPERATURE: float,
    DATA_KEYS.HEATER_VOLTAGE: float,
    DATA_KEYS.SUPPLY_VOLTAGE: float,
}
CONVERSION_TO_STRING = {
    DATA_KEYS.TIMESTAMP: '{0:' + TIMESTAMP_FMT + '}',
    DATA_KEYS.WIND_DIRECTION: '{0:.4f}',
    DATA_KEYS.WIND_SPEED: '{0:.4f}',
    DATA_KEYS.TEMPERATURE: '{0:.4f}',
    DATA_KEYS.HUMIDITY: '{0:.4f}',
    DATA_KEYS.PRESSURE: '{0:.4f}',
    DATA_KEYS.RAIN_ACCUMULATION: '{0:.4f}',
    DATA_KEYS.RAIN_DURATION: '{0:.4f}',
    DATA_KEYS.RAIN_INTENSITY: '{0:.4f}',
    DATA_KEYS.RAIN_PEAK_INTENSITY: '{0:.4f}',
    DATA_KEYS.HAIL_ACCUMULATION: '{0:.4f}',
    DATA_KEYS.HAIL_DURATION: '{0:.4f}',
    DATA_KEYS.HAIL_INTENSITY: '{0:.4f}',
    DATA_KEYS.HAIL_PEAK_INTENSITY: '{0:.4f}',
    DATA_KEYS.HEATER_TEMPERATURE: '{0:.4f}',
    DATA_KEYS.HEATER_VOLTAGE: '{0:.4f}',
    DATA_KEYS.SUPPLY_VOLTAGE: '{0:.4f}',
}
WeatherSample = namedtuple('WeatherSample', DATA_KEYS)


def parse_sample(s):
    row = s.split()
    sample = WeatherSample(
        TIMESTAMP=datetime.strptime(' '.join(row[4:-1]), '%d %b %Y %H:%M:%S'),
        **dict(
            (key, CONVERSION_TO_VALUE[key](row[i]))
            for i, key in enumerate(DATA_KEYS[1:])
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
    timestamp = average_datetimes([sample.timestamp for sample in samples])
    averaged = WeatherSample(
        timestamp=timestamp,
        **dict(
            (key, sum(getattr(sample, key) for sample in samples) / float(n))
            for key in DATA_KEYS[1:]
        )
    )

    return averaged


@fail_gracefully
@log_execution
def execute():
    samples = get_samples(n=WXT_SAMPLES)
    average = average_samples(samples)
    serialized = data.serialize(average, CONVERSION_TO_STRING)
    data.log_serialized(serialized, DATA_TAGS.WXT)
    queue_sbd(DATA_TAGS.WXT, serialized)


if __name__ == '__main__':
    execute()
