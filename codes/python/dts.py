from gpio import dts_off, dts_on
from time import sleep


def test():
    dts_on(1)
    sleep(60*8)
    dts_off(1)
