import re
from collections import namedtuple
from contextlib import closing
from datetime import datetime
from logging import getLogger
from time import time

from serial import Serial

import honcho.core.data as data
from honcho.config import (DATA_TAGS, GPIO, TIMESTAMP_FMT, WXT_BAUD, WXT_PORT,
                           WXT_SAMPLES, WXT_TIMEOUT)
from honcho.core.data import log_serialized, serialize
from honcho.core.gpio import powered
from honcho.tasks.common import task
from honcho.tasks.sbd import queue_sbd
from honcho.util import average_datetimes

logger = getLogger(__name__)

_DATA_KEYS = (
    "timestamp",
    "wind_direction",
    "wind_speed",
    "temperature",
    "humidity",
    "pressure",
    "rain_accumulation",
    "rain_duration",
    "rain_intensity",
    "rain_peak_intensity",
    "hail_accumulation",
    "hail_duration",
    "hail_intensity",
    "hail_peak_intensity",
    "heater_temperature",
    "heater_voltage",
    "supply_voltage",
)
DATA_KEYS = namedtuple("DATA_KEYS", (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
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
    DATA_KEYS.TIMESTAMP: "{0:" + TIMESTAMP_FMT + "}",
    DATA_KEYS.WIND_DIRECTION: "{0:.4f}",
    DATA_KEYS.WIND_SPEED: "{0:.4f}",
    DATA_KEYS.TEMPERATURE: "{0:.4f}",
    DATA_KEYS.HUMIDITY: "{0:.4f}",
    DATA_KEYS.PRESSURE: "{0:.4f}",
    DATA_KEYS.RAIN_ACCUMULATION: None,
    DATA_KEYS.RAIN_DURATION: None,
    DATA_KEYS.RAIN_INTENSITY: None,
    DATA_KEYS.RAIN_PEAK_INTENSITY: None,
    DATA_KEYS.HAIL_ACCUMULATION: None,
    DATA_KEYS.HAIL_DURATION: None,
    DATA_KEYS.HAIL_INTENSITY: None,
    DATA_KEYS.HAIL_PEAK_INTENSITY: None,
    DATA_KEYS.HEATER_TEMPERATURE: "{0:.4f}",
    DATA_KEYS.HEATER_VOLTAGE: "{0:.4f}",
    DATA_KEYS.SUPPLY_VOLTAGE: "{0:.4f}",
}
WeatherSample = namedtuple("WeatherSample", DATA_KEYS)

LINE_PATTERN = (
    r"0R0,"
    r"Dm=(?P<wind_direction>[\d\.]+).,"
    r"Sm=(?P<wind_speed>[\d\.]+).,"
    r"Ta=(?P<temperature>[\+\-\d\.]+).,"
    r"Ua=(?P<humidity>[\d\.]+).,"
    r"Pa=(?P<pressure>[\d\.]+).,"
    r"Rc=(?P<rain_accumulation>[\d\.]+).,"
    r"Rd=(?P<rain_duration>[\d\.]+).,"
    r"Ri=(?P<rain_intensity>[\d\.]+).,"
    r"Hc=(?P<hail_accumulation>[\d\.]+).,"
    r"Hd=(?P<hail_duration>[\d\.]+).,"
    r"Hi=(?P<hail_intensity>[\d\.]+).,"
    r"Rp=(?P<rain_peak_intensity>[\d\.]+).,"
    r"Hp=(?P<hail_peak_intensity>[\d\.]+).,"
    r"Th=(?P<heater_temperature>[\+\-\d\.]+).,"
    r"Vh=(?P<heater_voltage>[\+\-\d\.]+).,"
    r"Vs=(?P<supply_voltage>[\+\-\d\.]+)."
)


def parse_sample(s):
    row = re.search(LINE_PATTERN, s).groupdict()
    sample = WeatherSample(
        timestamp=datetime.now(),
        **dict((key, CONVERSION_TO_VALUE[key](value)) for key, value in row.items())
    )

    return sample


def get_samples(n=12):
    logger.debug("Getting {0} samples".format(n))
    samples = []
    start_time = time()
    with powered([GPIO.WXT]):
        with closing(Serial(WXT_PORT, WXT_BAUD, timeout=60)) as serial:
            while len(samples) < n and time() - start_time < WXT_TIMEOUT:
                line = serial.readline()
                logger.debug("Read line from vaisala: {0}".format(line))
                if re.search(LINE_PATTERN, line):
                    samples.append(parse_sample(line))
                    logger.debug("{0} of {1} samples collected".format(len(samples), n))

    return samples


def average_samples(samples):
    logger.debug("Averaging {0} samples".format(len(samples)))
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


def print_samples(samples):
    data.print_samples(samples, CONVERSION_TO_STRING)


@task
def execute():
    samples = get_samples(n=WXT_SAMPLES)
    average = average_samples(samples)
    serialized = serialize(average, CONVERSION_TO_STRING)
    log_serialized(serialized, DATA_TAGS.WXT)
    queue_sbd(serialized, DATA_TAGS.WXT)
