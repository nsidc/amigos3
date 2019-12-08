from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime

from pycampbellcr1000 import CR1000

from honcho.config import CR1000X_URL, SEP, DATA_TAGS, GPIO
from honcho.util import fail_gracefully, log_execution, serialize_datetime
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_data
from honcho.core.gpio import powered


_DATA_KEYS = (
    'timestamp',
    'Batt_volt',
    'Ptemp_C',
    'R6',
    'R10',
    'R20',
    'R40',
    'R2_5',
    'R4_5',
    'R6_5',
    'R8_5',
    'T6',
    'T10',
    'T20',
    'T40',
    'T2_5',
    'T4_5',
    'T6_5',
    'T8_5',
    'DT',
    'Q',
    'TCDT',
)
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
_VALUE_KEYS = DATA_KEYS[1:]
VALUE_KEYS = namedtuple('VALUE_KEYS', _VALUE_KEYS)(*_VALUE_KEYS)
STRING_CONVERSIONS = {
    VALUE_KEYS.TIMESTAMP: '{0:.4f}',
    VALUE_KEYS.BATT_VOLT: '{0:.4f}',
    VALUE_KEYS.PTEMP_C: '{0:.4f}',
    VALUE_KEYS.R6: '{0:.4f}',
    VALUE_KEYS.R10: '{0:.4f}',
    VALUE_KEYS.R20: '{0:.4f}',
    VALUE_KEYS.R40: '{0:.4f}',
    VALUE_KEYS.R2_5: '{0:.4f}',
    VALUE_KEYS.R4_5: '{0:.4f}',
    VALUE_KEYS.R6_5: '{0:.4f}',
    VALUE_KEYS.R8_5: '{0:.4f}',
    VALUE_KEYS.T6: '{0:.4f}',
    VALUE_KEYS.T10: '{0:.4f}',
    VALUE_KEYS.T20: '{0:.4f}',
    VALUE_KEYS.T40: '{0:.4f}',
    VALUE_KEYS.T2_5: '{0:.4f}',
    VALUE_KEYS.T4_5: '{0:.4f}',
    VALUE_KEYS.T6_5: '{0:.4f}',
    VALUE_KEYS.T8_5: '{0:.4f}',
    VALUE_KEYS.DT: '{0:.4f}',
    VALUE_KEYS.Q: '{0:.4f}',
    VALUE_KEYS.TCDT: '{0:.4f}',
}

Sample = namedtuple('Sample', _DATA_KEYS)


@contextmanager
def connection():
    device = CR1000.from_url(CR1000X_URL)

    if device.ping_node():
        yield
    else:
        raise Exception('CR1000X did not respond to ping')

    device.bye()


def get_last_sample():
    with powered([GPIO.HUB, GPIO.CRX]):
        with connection() as device:
            data = device.get_raw_packets("Public")
            fields = data[0]['RecFrag'][0]['Fields']
            fields['timestamp'] = datetime.now()  # TODO: should be in data
            sample = Sample(*fields)

    return sample


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.TIMESTAMP), sample.DEVICE_ID]
        + [STRING_CONVERSIONS[key].format(getattr(sample, key)) for key in VALUE_KEYS]
    )

    return serialized


@fail_gracefully
@log_execution
def execute():
    sample = get_last_sample()
    serialized = serialize(sample)
    log_data(serialized, DATA_TAGS.SBD)
    queue_sbd(DATA_TAGS.SBD, serialized)


if __name__ == '__main__':
    execute()
