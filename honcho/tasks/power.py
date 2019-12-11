import logging
from datetime import datetime
from collections import namedtuple

from honcho.util import fail_gracefully, log_execution, serialize_datetime
from honcho.core.onboard import get_voltage
from honcho.core.data import log_data
from honcho.config import MIN_SYSTEM_VOLTAGE, MAX_SYSTEM_SLEEP, SEP, DATA_TAGS
from honcho.core.system import system_standby

logger = logging.getLogger(__name__)


PowerSample = namedtuple('PowerSample', ('timestamp', 'voltage'))


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.timestamp), '{0:.2f}'.format(sample.voltage)]
    )

    return serialized


def voltage_check():
    sample = PowerSample(timestamp=datetime.now(), voltage=get_voltage())
    logger.info('Current voltage {0:.2f}'.format(sample.voltage))
    log_data(serialize(sample), DATA_TAGS.PWR)
    voltage_ok = sample.voltage >= MIN_SYSTEM_VOLTAGE
    if not voltage_ok:
        logger.warning(
            'System voltage {0} supply below minimum {1}'.format(
                sample.voltage, MIN_SYSTEM_VOLTAGE
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
