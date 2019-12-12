from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime

from pycampbellcr1000 import CR1000

from honcho.config import CR1000X_URL, DATA_TAGS, GPIO, TIMESTAMP_FMT
from honcho.util import fail_gracefully, log_execution
from honcho.tasks.sbd import queue_sbd
import honcho.core.data as data
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
CONVERSION_TO_STRING = {
    DATA_KEYS.TIMESTAMP: '{0:' + TIMESTAMP_FMT + '}',
    DATA_KEYS.BATT_VOLT: '{0:.4f}',
    DATA_KEYS.PTEMP_C: '{0:.4f}',
    DATA_KEYS.R6: '{0:.4f}',
    DATA_KEYS.R10: '{0:.4f}',
    DATA_KEYS.R20: '{0:.4f}',
    DATA_KEYS.R40: '{0:.4f}',
    DATA_KEYS.R2_5: '{0:.4f}',
    DATA_KEYS.R4_5: '{0:.4f}',
    DATA_KEYS.R6_5: '{0:.4f}',
    DATA_KEYS.R8_5: '{0:.4f}',
    DATA_KEYS.T6: '{0:.4f}',
    DATA_KEYS.T10: '{0:.4f}',
    DATA_KEYS.T20: '{0:.4f}',
    DATA_KEYS.T40: '{0:.4f}',
    DATA_KEYS.T2_5: '{0:.4f}',
    DATA_KEYS.T4_5: '{0:.4f}',
    DATA_KEYS.T6_5: '{0:.4f}',
    DATA_KEYS.T8_5: '{0:.4f}',
    DATA_KEYS.DT: '{0:.4f}',
    DATA_KEYS.Q: '{0:.4f}',
    DATA_KEYS.TCDT: '{0:.4f}',
}

CR1000XSample = namedtuple('CR1000XSample', DATA_KEYS)


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
            sample = CR1000XSample(**fields)

    return sample


@fail_gracefully
@log_execution
def execute():
    sample = get_last_sample()
    serialized = data.serialize(sample, CONVERSION_TO_STRING)
    data.log_serialized(serialized, DATA_TAGS.SBD)
    queue_sbd(DATA_TAGS.SBD, serialized)


if __name__ == '__main__':
    execute()
