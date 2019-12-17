from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from time import sleep

from pycampbellcr1000 import CR1000

from honcho.config import CRX_URL, DATA_TAGS, GPIO, TIMESTAMP_FMT, CRX_STARTUP_WAIT
from honcho.util import fail_gracefully, log_execution
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_serialized, serialize
from honcho.core.gpio import powered


DATA_CONFIG = (
    {'name': 'timestamp', 'to_str': '{0:' + TIMESTAMP_FMT + '}'},
    {'name': 'RecNbr', 'to_str': '{0:d}'},
    {'name': 'Batt_volt', 'to_str': '{0:.3f}'},
    {'name': 'Ptemp_C', 'to_str': '{0:.3f}'},
    {'name': 'R6', 'to_str': '{0:.4f}'},
    {'name': 'R10', 'to_str': '{0:.4f}'},
    {'name': 'R20', 'to_str': '{0:.4f}'},
    {'name': 'R40', 'to_str': '{0:.4f}'},
    {'name': 'R2_5', 'to_str': '{0:.4f}'},
    {'name': 'R4_5', 'to_str': '{0:.4f}'},
    {'name': 'R6_5', 'to_str': '{0:.4f}'},
    {'name': 'R8_5', 'to_str': '{0:.4f}'},
    {'name': 'T6', 'to_str': '{0:.6f}'},
    {'name': 'T10', 'to_str': '{0:.6f}'},
    {'name': 'T20', 'to_str': '{0:.6f}'},
    {'name': 'T40', 'to_str': '{0:.6f}'},
    {'name': 'T2_5', 'to_str': '{0:.6f}'},
    {'name': 'T4_5', 'to_str': '{0:.6f}'},
    {'name': 'T6_5', 'to_str': '{0:.6f}'},
    {'name': 'T8_5', 'to_str': '{0:.6f}'},
    {'name': 'DT', 'to_str': '{0}'},  #  Check
    {'name': 'Q', 'to_str': '{0}'},  #  Check
    {'name': 'TCDT', 'to_str': '{0}'},  #  Check
)
_DATA_KEYS = [el['name'] for el in DATA_CONFIG]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
CONVERSION_TO_STRING = dict((el['name'], el['to_str']) for el in DATA_CONFIG)

CRXSample = namedtuple('CRXSample', DATA_KEYS)


@contextmanager
def connection():
    device = CR1000.from_url(CRX_URL)

    if device.ping_node():
        yield device
    else:
        raise Exception('CRX did not respond to ping')

    device.bye()


def get_last_sample():
    with powered([GPIO.HUB, GPIO.CRX]):
        sleep(CRX_STARTUP_WAIT)
        with connection() as device:
            data = device.get_data("Public")[-1]
            data['timestamp'] = data['Datetime']
            del data['Datetime']
            sample = CRXSample(**data)

    return sample


@fail_gracefully
@log_execution
def execute():
    sample = get_last_sample()
    serialized = serialize(sample, CONVERSION_TO_STRING)
    log_serialized(serialized, DATA_TAGS.CRX)
    queue_sbd(serialized, DATA_TAGS.CRX)


if __name__ == '__main__':
    execute()
