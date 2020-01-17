from collections import namedtuple
from contextlib import contextmanager
from time import sleep
from datetime import datetime
import logging

from pycampbellcr1000 import CR1000

from honcho.config import CRX_URL, DATA_TAGS, GPIO, TIMESTAMP_FMT, CRX_STARTUP_WAIT
from honcho.tasks.sbd import queue_sbd
from honcho.core.data import log_serialized, serialize
from honcho.core.gpio import powered
from honcho.tasks.common import task


DATA_CONFIG = (
    {'name': 'timestamp', 'to_str': '{0:' + TIMESTAMP_FMT + '}'},
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
    {'name': 'DT', 'to_str': '{0:.6f}'},
    {'name': 'Q', 'to_str': '{0}'},
    {'name': 'TCDT', 'to_str': '{0:.6f}'},
)
_DATA_KEYS = [el['name'] for el in DATA_CONFIG]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
CONVERSION_TO_STRING = dict((el['name'], el['to_str']) for el in DATA_CONFIG)

CRXSample = namedtuple('CRXSample', DATA_KEYS)


logger = logging.getLogger(__name__)
logging.getLogger('pylink').setLevel(logging.ERROR)
logging.getLogger('pycampbellcr1000').setLevel(logging.ERROR)


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
        logger.debug('Waiting {0} seconds for crx startup'.format(CRX_STARTUP_WAIT))
        sleep(CRX_STARTUP_WAIT)
        with connection() as device:
            logger.debug('Getting last sample from CRX')
            recfrag = device.get_raw_packets("Public")[-1]['RecFrag'][-1]
            data = {'timestamp': datetime.now()}
            data.update(**recfrag['Fields'])
            sample = CRXSample(**data)

    return sample


@task
def execute():
    sample = get_last_sample()
    serialized = serialize(sample, CONVERSION_TO_STRING)
    log_serialized(serialized, DATA_TAGS.CRX)
    queue_sbd(serialized, DATA_TAGS.CRX)
