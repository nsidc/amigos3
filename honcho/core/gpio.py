import subprocess as subprocess

INDEX_DEVICE = "/sys/class/gpio/pwr_ctl/index"
DATA_DEVICE = "/sys/class/gpio/pwr_ctl/data"

GPIO = {
    'sbd': {'index': 0, 'mask': int('0b00000001', 2)},
    'gps': {'index': 0, 'mask': int('0b00000010', 2)},
    'imm': {'index': 0, 'mask': int('0b00000100', 2)},
    'wxt': {'index': 0, 'mask': int('0b00001000', 2)},
    'crx': {'index': 0, 'mask': int('0b00010000', 2)},
    # '-': {'index': 0, 'mask': int('0b00100000', 2)},
    'win': {'index': 0, 'mask': int('0b01000000', 2)},
    # '-': {'index': 0, 'mask': int('0b00100000', 2)},
    'dts': {'index': 1, 'mask': int('0b00000001', 2)},
    'cam': {'index': 1, 'mask': int('0b00000010', 2)},
    'rtr': {'index': 1, 'mask': int('0b00000100', 2)},
    'hub': {'index': 1, 'mask': int('0b00001000', 2)},
    'ird': {'index': 1, 'mask': int('0b00010000', 2)},
    # '-': {'index': 1, 'mask': int('0b00100000', 2)},
    # '-': {'index': 1, 'mask': int('0b01000000', 2)},
    # '-': {'index': 1, 'mask': int('0b10000000', 2)},
    'v5e': {'index': 2, 'mask': int('0b00000001', 2)},
    'ser': {'index': 2, 'mask': int('0b00000010', 2)},
    # '-': {'index': 2, 'mask': int('0b00000100', 2)},
    'sol': {'index': 2, 'mask': int('0b00001000', 2)},
    # '-': {'index': 2, 'mask': int('0b00010000', 2)},
    # '-': {'index': 2, 'mask': int('0b00100000', 2)},
    # '-': {'index': 2, 'mask': int('0b01000000', 2)},
    # '-': {'index': 2, 'mask': int('0b10000000', 2)},
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


def _on(key):
    set_mask(GPIO[key]['index'], GPIO[key]['mask'])


def _off(key):
    unset_mask(GPIO[key]['index'], GPIO[key]['mask'])


def hub_on():
    _on('hub')


def hub_off():
    _off('hub')


def gps_on():
    _on('gps')


def gps_off():
    _off('gps')


def sbd_on():
    _on('sbd')


def sbd_off():
    _off('sbd')


def weather_on():
    _on('wxt')


def weather_off():
    _off('wxt')


def imm_on():
    _on('imm')


def imm_off():
    _off('imm')


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
    _on('v5e')


def V5_ENA_OFF():
    _off('v5e')


def solar_on():
    _on('sol')


def solar_off():
    _off('sol')


def cr1000_on():
    _on('crx')


def cr1000_off():
    _off('crx')


def router_on():
    _on('rtr')


def router_off():
    _off('rtr')


def iridium_on():
    _on('ird')


def iridium_off():
    _off('ird')


def dts_on():
    _on('dts')


def dts_off():
    _off('dts')


def cam_on():
    _on('cam')


def cam_off():
    _off('cam')


def win_on():
    _on('win')


def win_off():
    _off('win')


def enable_serial():
    _on('ser')


def disable_serial():
    _off('ser')
