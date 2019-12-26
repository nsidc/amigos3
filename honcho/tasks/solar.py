from time import sleep
from datetime import datetime
from logging import getLogger
from collections import namedtuple

from honcho.util import average_datetimes
from honcho.core.gpio import powered
from honcho.tasks.common import task
from honcho.config import (
    SOLAR_SAMPLES,
    SOLAR_SAMPLE_WAIT,
    DATA_TAGS,
    TIMESTAMP_FMT,
    GPIO,
)
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_serialized, serialize
from honcho.core.onboard import get_solar

logger = getLogger(__name__)

DATA_CONFIG = (
    {'name': 'timestamp', 'to_str': '{0:' + TIMESTAMP_FMT + '}'},
    {'name': 'solar_up', 'to_str': '{0}'},
    {'name': 'solar_down', 'to_str': '{0}'},
)
_DATA_KEYS = [el['name'] for el in DATA_CONFIG]
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
CONVERSION_TO_STRING = dict((el['name'], el['to_str']) for el in DATA_CONFIG)

SolarSample = namedtuple('SolarSample', DATA_KEYS)


def get_samples(n=SOLAR_SAMPLES, wait=SOLAR_SAMPLE_WAIT):
    samples = []
    with powered([GPIO.SOL]):
        for _ in xrange(n):
            timestamp = datetime.now()
            samples.append(SolarSample(timestamp, *get_solar()))
            sleep(SOLAR_SAMPLE_WAIT)

    return samples


def average_samples(samples):
    logger.debug('Averaging {0} samples'.format(len(samples)))
    n = len(samples)
    timestamp = average_datetimes([sample.timestamp for sample in samples])
    averaged = SolarSample(
        timestamp=timestamp,
        **dict(
            (key, sum(getattr(sample, key) for sample in samples) / float(n))
            for key in (set(DATA_KEYS) - set([DATA_KEYS.TIMESTAMP]))
        )
    )

    return averaged


@task
def execute():
    samples = get_samples(n=SOLAR_SAMPLES, wait=SOLAR_SAMPLE_WAIT)
    average = average_samples(samples)
    serialized = serialize(average, CONVERSION_TO_STRING)
    log_serialized(serialized, DATA_TAGS.SOL)
    queue_sbd(serialized, DATA_TAGS.SOL)
