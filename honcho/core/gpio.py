from contextlib import contextmanager
from time import sleep

from honcho.config import INDEX_DEVICE, DATA_DEVICE, GPIO_CONFIG


def set_index(index):
    with open(INDEX_DEVICE, "wb") as f:
        f.write(hex(index))


def get_value(index):
    set_index(index)
    with open(DATA_DEVICE, "rb") as f:
        return int(f.read().strip(), 16)


def set_mask(index, mask):
    value = get_value(index)
    new_value = value | mask

    set_index(index)
    with open(DATA_DEVICE, "wb") as f:
        f.write(hex(new_value))


def unset_mask(index, mask):
    value = get_value(index)
    new_value = value & ~mask

    set_index(index)
    with open(DATA_DEVICE, "wb") as f:
        f.write(hex(new_value))


def turn_on(component):
    set_mask(GPIO_CONFIG[component]['index'], GPIO_CONFIG[component]['mask'])


def turn_off(component):
    unset_mask(GPIO_CONFIG[component]['index'], GPIO_CONFIG[component]['mask'])


def is_on(component):
    index = GPIO_CONFIG[component]['index']
    mask = GPIO_CONFIG[component]['mask']
    set_index(index)
    value = get_value(mask)
    result = bool(value & mask)

    return result


@contextmanager
def powered(components):
    for component in components:
        if is_on(component):
            raise Exception('{0} requested but already powered on')
        turn_on(component)
        sleep(GPIO_CONFIG[component]['wait'])

    yield

    for component in components:
        turn_off(component)


def all_off():
    for index in range(3):
        unset_mask(index, 255)
