from serial import Serial as ser
from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
from time import sleep
from execp import printf
import ftplib as ftp

from solar import solar_live 
from vaisala import Average_Reading
from cr1000x import cr1000x




class dial_in():
    def __init__(self, *args, **kwargs):
        pass

    def find_files(self):
        pass

    def send(self):
        pass

    def dialin(self):
        router_off(1)
        modem_on(1)
        sleep(1)
        iridium_on(1)
        sleep(60*20)
        iridium_off(1)
        router_off(1)


class dial_out():
    def __init__(self, *args, **kwargs):
        pass

    def find_files(self):
        pass

    def send(self):
        pass

    def dialout(self):
        router_on(1)
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
        enable_serial()
        sleep(1)
        message_sent = False
    except:
        printf('Unable to open port')
    else:
        port.write(message + '\r')
        printf('sent SBD message: {0} {1}'.format(message, '\r'))
        sleep(60)
        message_sent = True
    finally:
        disable_serial()
        sbd_off(1)
        iridium_off(1)
    return message_sent


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

def device_data_sbd():
    #instances of classes
    solarclass = solar_live()
    vaisalaclass = Average_Reading()
    crclass = cr1000x()

    #variables to store dictionary strings 
    solar = solarclass.solar_iridium() # Returns dictionary of live data 1 and data 2, the readings from each of the light sensors 
    vaisala = vaisalaclass.vaisala_iridium() # Returns array of 2-minute averaged weather data dictionary 
    cr = crclass.cr_iridium() # Returns array of all live CR data in dictionary string 

    #call send function with new message
    message_sent = send(message=solar)
    if message_sent == True:
        print('Solar message successfully sent')
        message_sent = send(message=vaisala)
        if message_sent == True:
            print('Vaiala message successfully sent')
            message_sent = send(message=cr)
            if message_sent == True:
                print('CR message successfully sent')
            else:
                print('CR message did not sent over iridium')
        else:
            print('Vaisala message did not send over iridium')
    else:
        print('Solar message did not send over iridium')


if __name__ == "__main__":
    device_data_sbd()