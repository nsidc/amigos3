from honcho.config import (HUMIDITY_DATA_DEVICE, SUPPLY_DATA_DEVICE,
                           SUPPLY_INDEX_DEVICE, TEMPERATURE_DATA_DEVICE,
                           VOLTAGE_CONVERTER)


def _set_supply_index(index):
    with open(SUPPLY_INDEX_DEVICE, "wb") as f:
        f.write(hex(index))


def _get_supply_value(index):
    _set_supply_index(index)
    with open(SUPPLY_DATA_DEVICE, "rb") as f:
        return int(f.read().strip(), 16)


def get_raw_voltage():
    raw = _get_supply_value(4)

    return raw


def get_raw_current():
    raw = _get_supply_value(5)

    return raw


def get_raw_humidity():
    with open(HUMIDITY_DATA_DEVICE, "rb") as f:
        return int(f.read().strip(), 16)


def get_raw_temperature():
    with open(TEMPERATURE_DATA_DEVICE, "rb") as f:
        return int(f.read().strip(), 16)


def get_voltage():
    raw = get_raw_voltage()

    return VOLTAGE_CONVERTER(raw)


def get_current():
    raw = get_raw_current()

    return raw


def get_humidity():
    raw = get_raw_humidity()

    return raw


def get_temperature():
    raw = get_raw_temperature()

    return raw


def get_solar():
    solar_1 = _get_supply_value(0)
    solar_2 = _get_supply_value(1)

    return (solar_1, solar_2)
