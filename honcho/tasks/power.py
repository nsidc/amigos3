import logging
from datetime import datetime
from collections import namedtuple

from honcho.util import fail_gracefully, log_execution, serialize_datetime
from honcho.core.onboard import get_voltage
from honcho.core.data import log_data
from honcho.config import MIN_SYSTEM_VOLTAGE, MAX_SYSTEM_SLEEP, SEP, DATA_TAGS
from honcho.core.system import system_standby

logger = logging.getLogger(__name__)


_DATA_KEYS = ('TIMESTAMP', 'VOLTAGE')
_VALUE_KEYS = _DATA_KEYS[1:]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
VALUE_KEYS = namedtuple('VALUE_KEYS', _VALUE_KEYS)(*_VALUE_KEYS)
VALUE_CONVERSIONS = {VALUE_KEYS.VOLTAGE: float}
STRING_CONVERSIONS = {VALUE_KEYS.VOLTAGE: '{0:.2f}'}
SAMPLE = namedtuple('SAMPLE', DATA_KEYS)


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.TIMESTAMP)]
        + [STRING_CONVERSIONS[key].format(getattr(sample, key)) for key in VALUE_KEYS]
    )

    return serialized


def voltage_check():
    voltage_sample = SAMPLE(TIMESTAMP=datetime.now(), VOLTAGE=get_voltage())
    logger.info('Current voltage {0}'.format(voltage_sample.VOLTAGE))
    log_data(serialize(voltage_sample), DATA_TAGS.PWR)
    voltage_ok = voltage_sample.voltage >= MIN_SYSTEM_VOLTAGE
    if not voltage_ok:
        logger.warning(
            'System voltage {0} supply below minimum {1}'.format(
                voltage_sample.VOLTAGE, MIN_SYSTEM_VOLTAGE
            )
        )
        system_standby(MAX_SYSTEM_SLEEP)

    return voltage_ok


@fail_gracefully
@log_execution
def execute():
    voltage_check()


if __name__ == '__main__':
    execute()
