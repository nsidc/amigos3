#Sid Arora
#Updated as of 8/6/19
#Script will read in ascii data from aquadopp

from serial import Serial as ser
from time import sleep

def read_aquadopp():
    port = ser("/dev/ttyS4")
    port.baudrate = 9600
    port.flushInput()
    port.write("FCL\r\n")
    sleep(3)
    port.write("FCL\r\n")
    sleep(3)
    print(port.read(port.inWaiting()))
    port.flushInput()
    sleep(3)
    port.write("!00SampleGetList\r\n")
    sleep(3)
    summary = port.read(port.inWaiting())
    print("The following newest sample will be recorded: " + summary[73:81])
    print(port.read(port.inWaiting()))
    port.flushInput()
    sleep(3)
    port.write("!00SAMPLEGETDATA:" + summary[73:81] + "\r\n")
    sleep(3) 
    aquadopp_raw_data = port.read(port.inWaiting())
    port.flushInput()
    sleep(3) 
    return aquadopp_raw_data

def clean_data():
    raw_data = read_aquadopp()

if __name__ == "__main__":
    read_aquadopp()

