import logging
from contextlib import contextmanager

from honcho.config import (
    POWER_INDEX_DEVICE,
    POWER_DATA_DEVICE,
    GPIO_CONFIG,
    HUB_ALWAYS_ON,
    GPIO,
)

logger = logging.getLogger(__name__)


def _set_index(index):
    with open(POWER_INDEX_DEVICE, "wb") as f:
        f.write(hex(index))


def _get_value(index):
    _set_index(index)
    with open(POWER_DATA_DEVICE, "rb") as f:
        return int(f.read().strip(), 16)


def _set_mask(index, mask):
    value = _get_value(index)
    new_value = value | mask

    _set_index(index)
    with open(POWER_DATA_DEVICE, "wb") as f:
        f.write(hex(new_value))


def _unset_mask(index, mask):
    value = _get_value(index)
    new_value = value & ~mask

    _set_index(index)
    with open(POWER_DATA_DEVICE, "wb") as f:
        f.write(hex(new_value))


def turn_on(component):
    _set_mask(GPIO_CONFIG[component]['index'], GPIO_CONFIG[component]['mask'])


def turn_off(component):
    _unset_mask(GPIO_CONFIG[component]['index'], GPIO_CONFIG[component]['mask'])


def is_on(component):
    index = GPIO_CONFIG[component]['index']
    mask = GPIO_CONFIG[component]['mask']
    value = _get_value(index)
    result = bool(value & mask)

    return result


def list():
    for component in GPIO:
        print('{0}: {1}'.format(component, 'ON' if is_on(component) else 'OFF'))


@contextmanager
def powered(components):
    for component in components:
        if is_on(component):
            logger.debug('Already on: {0}'.format(component))
        else:
            logger.debug('Turning on: {0}'.format(component))
            turn_on(component)
    try:
        yield
    finally:
        for component in components:
            if component == GPIO.HUB and HUB_ALWAYS_ON:
                logger.debug('Leaving on: {0}'.format(component))
                continue
            logger.debug('Turning off {0}'.format(component))
            turn_off(component)


def set_awake_gpio_state():
    if HUB_ALWAYS_ON and not is_on(GPIO.HUB):
        turn_on(GPIO.HUB)


def all_off():
    for index in range(3):
        _unset_mask(index, 255)
