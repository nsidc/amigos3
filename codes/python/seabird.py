#Sid Arora
#Updated as of 8/6/19
#Script will read in SeaBird data and translate to clean file format 

from serial import Serial as ser
from time import sleep

def read_seabird():
    port = ser("/dev/ttyS4")
    port.baudrate = 9600
    port.flushInput()
    port.write("GetCD\r\n")
    sleep(3)
    print(port.read(port.inWaiting()))
    port.write("GetCD\r\n")
    sleep(3)
    print(port.read(port.inWaiting()))
    port.write("FCL\r\n")
    sleep(3)
    print(port.read(port.inWaiting()))
    port.write("SendWakeUpTone\r\n")
    sleep(3)
    print(port.read(port.inWaiting()))
    port.write("#90TS\r\n")
    sleep(5)
    seabird_raw_data = port.read(port.inWaiting())
    return seabird_raw_data

if __name__ == "__main__":
    read_seabird()