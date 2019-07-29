from serial import Serial as ser
#from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
from time import sleep
from execp import printf
#import ftplib as ftp

#from solar import solar_live 
#from vaisala import Average_Reading
#from cr1000x import cr1000x




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

def sbd():
    #instances of classes
    #solarclass = solar_live()
    #vaisalaclass = Average_Reading()
    #crclass = cr1000x()

    #variables to store dictionary strings 
    #solar = solarclass.solar_sbd() # Returns dictionary of live data 1 and data 2, the readings from each of the light sensors 
    #vaisala = vaisalaclass.vaisala_sbd() # Returns array of 2-minute averaged weather data dictionary 
    #cr = crclass.cr_sbd() # Returns array of all live CR data in dictionary string 

    solar = "Iridium Test YEEEET"
    vaisala = "Still testing... lol"
    cr = "...sigh..."

    #Commands send to iridium solar data
    message_sent = False
    sbd_port = ser("/dev/ttyUSB0")
    sbd_port.flushInput()
    sbd_port.write("AT\r\n")
    sleep(2)
    check = sbd_port.read(sbd_port.inWaiting())
    if check.find("OK") != -1:
        sbd_port.write("AT&K0\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT+SBDWT={0}\r\n".format(solar))
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDIX\r\n")
                sleep(15)
                array = sbd_port.read(sbd_port.inWaiting())
                array1 = array.split(":")[1].split(",")
                if array1[0] == " 0":
                    message_sent = True
                    printf("solar message sent successfully, moving to vaisala")
            else:
                printf("AT+SBDWT message command did not work to the iridium (Solar)")
        else:
            printf("AT&K0 command did not work to the iridium (Solar)")
    else:
        printf("AT command did not work to the iridium (Solar)")

    #Commands send to iridium vaisala data
    if message_sent == True:
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(vaisala))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                        printf("vaisala message sent successfully, moving to cr")
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Vaisala)")
            else:
                printf("AT&K0 command did not work to the iridium (Vaisala)")
        else:
            printf("AT command did not work to the iridium (Vaisala)")
    else:
        printf("solar data did not send, still moving on to vaisala ")
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(vaisala))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                        printf("vaisala message sent successfully, moving to cr")
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Vaisala)")
            else:
                printf("AT&K0 command did not work to the iridium (Vaisala)")
        else:
            printf("AT command did not work to the iridium (Vaisala)")

    #Commands send to iridium cr data
    if message_sent == True:
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(cr))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                        printf("cr message sent successfully, moving to (insert next device)")
                else:
                    printf("AT+SBDWT message command did not work to the iridium (CR)")
            else:
                printf("AT&K0 command did not work to the iridium (CR)")
        else:
            printf("AT command did not work to the iridium (CR)")
    else:
        printf("vaisala data did not send, still moving to cr")
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(cr))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                        printf("cr message sent successfully, moving to (insert next device)")
                else:
                    printf("AT+SBDWT message command did not work to the iridium (CR)")
            else:
                printf("AT&K0 command did not work to the iridium (CR)")
        else:
            printf("AT command did not work to the iridium (CR)")


if __name__ == "__main__":
    sbd()