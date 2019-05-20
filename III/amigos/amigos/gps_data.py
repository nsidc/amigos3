import pynmea2 as nmea
from serial import Serial as ser
from time import sleep


def getRaw_data():
    try:
        port = ser('/dev/ttyS0')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print 'Can not open port'
        return 0, 0
    GPVTG = None
    GPGGA = None
    while GPGGA is None or GPVTG is None:
        data = port.readline()
        try:
            if data.find('GPVTG') != -1:
                GPVTG = data
            elif data.find('GPGGA') != -1:
                GPGGA = data
        except:
            print("Unable to read. Check GPS module configuration or try again")
            port.close()
            return 0, 0
        sleep(1)
    port.close()
    print(GPGGA)
    print(GPVTG)
    return GPGGA, GPVTG


def Nmea_parse():
    GPGGA, GPVTG = getRaw_data()
    GPGGA_parser = None
    GPVTG_parser = None
    if GPGGA and GPVTG:
        GPGGA_parser = nmea.parse(GPGGA)
        GPVTG_parser = nmea.parse(GPVTG)
    return GPGGA_parser, GPVTG_parser


if __name__ == "__main__":
    print(Nmea_parse())
