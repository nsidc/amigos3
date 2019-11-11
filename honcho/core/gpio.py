import subprocess as subprocess
from contextlib import contextmanager

INDEX_DEVICE = "/sys/class/gpio/pwr_ctl/index"
DATA_DEVICE = "/sys/class/gpio/pwr_ctl/data"

GPIO = {
    'sbd': {'index': 0, 'mask': int('0b00000001', 2), 'wait': 5},
    'gps': {'index': 0, 'mask': int('0b00000010', 2), 'wait': 5},
    'imm': {'index': 0, 'mask': int('0b00000100', 2), 'wait': 5},
    'wxt': {'index': 0, 'mask': int('0b00001000', 2), 'wait': 5},
    'crx': {'index': 0, 'mask': int('0b00010000', 2), 'wait': 5},
    # '-': {'index': 0, 'mask': int('0b00100000', 2), 'wait': 5},
    'win': {'index': 0, 'mask': int('0b01000000', 2), 'wait': 5},
    # '-': {'index': 0, 'mask': int('0b00100000', 2), 'wait': 5},
    'dts': {'index': 1, 'mask': int('0b00000001', 2), 'wait': 5},
    'cam': {'index': 1, 'mask': int('0b00000010', 2), 'wait': 5},
    'rtr': {'index': 1, 'mask': int('0b00000100', 2), 'wait': 5},
    'hub': {'index': 1, 'mask': int('0b00001000', 2), 'wait': 5},
    'ird': {'index': 1, 'mask': int('0b00010000', 2), 'wait': 5},
    # '-': {'index': 1, 'mask': int('0b00100000', 2), 'wait': 5},
    # '-': {'index': 1, 'mask': int('0b01000000', 2), 'wait': 5},
    # '-': {'index': 1, 'mask': int('0b10000000', 2), 'wait': 5},
    'v5e': {'index': 2, 'mask': int('0b00000001', 2), 'wait': 5},
    'ser': {'index': 2, 'mask': int('0b00000010', 2), 'wait': 5},
    # '-': {'index': 2, 'mask': int('0b00000100', 2), 'wait': 5},
    'sol': {'index': 2, 'mask': int('0b00001000', 2), 'wait': 5},
    # '-': {'index': 2, 'mask': int('0b00010000', 2), 'wait': 5},
    # '-': {'index': 2, 'mask': int('0b00100000', 2), 'wait': 5},
    # '-': {'index': 2, 'mask': int('0b01000000', 2), 'wait': 5},
    # '-': {'index': 2, 'mask': int('0b10000000', 2), 'wait': 5},
}


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
    set_mask(GPIO[component]['index'], GPIO[component]['mask'])


def turn_off(component):
    unset_mask(GPIO[component]['index'], GPIO[component]['mask'])


def is_on(component):
    index = GPIO[component]['index']
    mask = GPIO[component]['mask']
    set_index(index)
    value = get_value(mask)
    result = bool(value & mask)

    return result


@contextmanager
def powered(component):
    if is_on(component):
        raise Exception('{0} requested but already powered on')
    turn_on(component)
    sleep(GPIO[component]['wait'])
    yield
    turn_off(component)


def hub_on():
    turn_on('hub')


def hub_off():
    turn_off('hub')


def gps_on():
    turn_on('gps')


def gps_off():
    turn_off('gps')


def sbd_on():
    turn_on('sbd')


def sbd_off():
    turn_off('sbd')


def weather_on():
    turn_on('wxt')


def weather_off():
    turn_off('wxt')


def imm_on():
    turn_on('imm')


def imm_off():
    turn_off('imm')


def all_off():
    for index in range(3):
        unset_mask(index, 255)


def shutdown():
    all_off()
    subprocess.call("shutdown -h now", shell=True)


def reboot():
    all_off()
    subprocess.call("reboot", shell=True)


def V5_ENA_ON():
    turn_on('v5e')


def V5_ENA_OFF():
    turn_off('v5e')


def solar_on():
    turn_on('sol')


def solar_off():
    turn_off('sol')


def cr1000_on():
    turn_on('crx')


def cr1000_off():
    turn_off('crx')


def router_on():
    turn_on('rtr')


def router_off():
    turn_off('rtr')


def iridium_on():
    turn_on('ird')


def iridium_off():
    turn_off('ird')


def dts_on():
    turn_on('dts')


def dts_off():
    turn_off('dts')


def cam_on():
    turn_on('cam')


def cam_off():
    turn_off('cam')


def win_on():
    turn_on('win')


def win_off():
    turn_off('win')


def enable_serial():
    turn_on('ser')


def disable_serial():
    turn_off('ser')
