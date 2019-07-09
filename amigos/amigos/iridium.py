from serial import Serial as ser
from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on
from time import sleep


def send(message):
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 9600
        port.open()
        port.flushInput()
        sbd_on(1)
        sleep(1)
        enable_serial()
        sleep(1)
    except:
        print('Unable to open port')
    else:
        port.write(message)
        rv = read()
        return rv
    finally:
        disable_serial()
        sbd_off(1)


def read():
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 9600
        port.open()
    except:
        print('Unable to open port')
        return None
    rev = port.read(port.inWaiting())
    return rev
