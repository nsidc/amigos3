from contextlib import contextmanager
from time import sleep

from honcho.config import POWER_INDEX_DEVICE, POWER_DATA_DEVICE, GPIO_CONFIG


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
    _set_index(index)
    value = _get_value(mask)
    result = bool(value & mask)

    return result


@contextmanager
def powered(components):
    for component in components:
        if is_on(component):
            raise Exception('{0} requested but already powered on'.format(component))
        turn_on(component)
        sleep(GPIO_CONFIG[component]['wait'])
    try:
        yield
    finally:
        for component in components:
            turn_off(component)


def all_off():
    for index in range(3):
        _unset_mask(index, 255)
