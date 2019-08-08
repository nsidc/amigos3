# Sid Arora
# Updated as of 8/6/19
# Script will read in SeaBird data and translate to clean file format

from serial import Serial as ser
from time import sleep
from execp import printf
from gpio import disable_serial, enable_serial
from monitor import reschedule


def read_seabird():
    printf("Started Sea Bird data acquisition")
    enable_serial()
    try:
        port = ser("/dev/ttyS4")
        port.timeout = 60
        port.baudrate = 9600
        port.flushInput()
        port.write("GetCD\r\n")
        sleep(3)
        # print(port.read(port.inWaiting()))
        port.write("GetCD\r\n")
        sleep(3)
        # print(port.read(port.inWaiting()))
        port.write("FCL\r\n")
        sleep(3)
        # print(port.read(port.inWaiting()))
        port.write("SendWakeUpTone\r\n")
        sleep(3)
        # print(port.read(port.inWaiting()))
        port.write("#90TS\r\n")
        sleep(5)
        seabird_raw_data = port.read(port.inWaiting())
        reschedule(run="read_seabird")
    except:
        reschedule(re="read_seabird")
    finally:
        disable_serial()
    printf("All done with Sea Bird")
    return seabird_raw_data


if __name__ == "__main__":
    read_seabird()
