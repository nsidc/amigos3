from serial import Serial as ser
from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on, router_off, router_on
from time import sleep
from execp import printf


def dialin():
    router_off(1)
    sleep(1)
    iridium_off(1)
    sleep(60*20)
    iridium_off(1)
    router_off(1)


def dialout():
    router_off(1)
    sleep(1)
    iridium_on(1)
    sleep(60)
    iridium_off(1)
    router_off(1)


def send(message="Testing"):
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 9600
        port.open()
        iridium_on(1)
        sbd_on(1)
        sleep(1)
        iridium_off(1)
        enable_serial()
        sleep(1)
    except:
        printf('Unable to open port')
    else:
        port.write(message + '\r')
        printf('sent SBD message: {0} {1}'.format(message, '\r'))
        sleep(60)
    finally:
        disable_serial()
        sbd_off(1)
        iridium_off(1)


def read():
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 9600
        port.timeout = 60
        port.open()
    except:
        printf('Unable to open port')
        return None
    rev = port.read(port.inWaiting())
    return rev
