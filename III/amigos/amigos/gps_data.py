import pynmea2 as nmea
from serial import Serial as ser
from time import sleep
# import binascii as bina
from gpio import gps_off, gps_on
from radium import read, send


def __writeFile(file_name, strings, form):
    with open(file_name, form) as fil:
        fil.write(strings)
        print('Writing data')
    return True


def __getRaw_data():
    """
    Read raw data in nmea format from the GPS module.
    Take not argument
    Return the GPGGA, GPVTG variable
    """
    try:
        port = ser('/dev/ttyS0')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print('Unable to open port')
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
    return GPGGA, GPVTG


def __Nmea_parse():
    """
    Parser the nmea language code into human readable location code
    Take no argument
    Return  GPGGA_parser, GPVTG_parser
    """
    GPGGA, GPVTG = __getRaw_data()
    GPGGA_parser = None
    GPVTG_parser = None
    if GPGGA and GPVTG:
        GPGGA_parser = nmea.parse(GPGGA)
        GPVTG_parser = nmea.parse(GPVTG)
    # print(GPGGA_parser, GPVTG_parser)
    return GPGGA_parser, GPVTG_parser


def quick_gps_data():
    gps_data = __Nmea_parse()
    Altitude = gps_data[0].altitude
    Longitude = gps_data[0].lon
    Longitude_Dir = gps_data[0].lon_dir
    Latitude = gps_data[0].lat
    Latitude_Dir = gps_data[0].lat_dir
    print(" Altitude: {0}\n Longitude: {1}\n Longitude Dir: {2}\n Latitude: {3}\n Latitude Dir: {4}\n".format(
        Altitude, Longitude, Longitude_Dir, Latitude, Latitude_Dir))


def get_binex(inter=15, time=15):
    try:
        port = ser('/dev/ttyS0')
        port.baudrate = 115200
        port.open()
        port.flushInput()
        port.timeOut = None
    except:
        print('Unable to open port')
        return
    gps_on(bit=1)
    sleep(10)
    savee = False
    seq = 1
    while seq <= time*60/inter:
        keys = ('GGA', 'GLL', 'GMP', 'GNS', 'GRS', 'GSA', 'GST', 'GSV',
                'HDT', 'RMC', 'ROT', 'VTG', 'ZDA', 'UID', 'ATT')
        is_byte = False
        while not is_byte:
            byte = port.readline()
            # print(byte)
            key = 0
            for key, objects in enumerate(keys):
                if byte.find(objects) != 3:
                    if byte.find(objects) == -1 and key == 14 and byte.find("\r\n") == -1:
                        # print(1, byte)
                        if byte != '\n' or byte != '':
                            savee = __writeFile('gps_binex_data.log', byte, 'ab')
                            sleep(1)
                            break
                    elif byte.find(objects) == 3:
                        # print(byte, key, byte.find(objects))
                        break
                    elif byte.find(objects) == -1:
                        pass
                    else:
                        # print(2, byte)
                        byte = byte[0:int(byte.find(objects))-3]
                        if byte == '$PTP' or byte.find('ATT') != -1:
                            break
                        elif byte or byte != '\n':
                            # print(3, byte)
                            savee = __writeFile('gps_binex_data.log', byte, 'ab')
                            sleep(1)
                            is_byte = True
                            break
                if savee == True and byte.find('GGA') != -1:
                    is_byte = True
                    seq = seq+1
                    savee = False
                    # print(seq, savee)
                    sleep(inter)
                    break

    port.close()
    gps_off(bit=1)


def get_nmea(inter=15, time=15):
    try:
        port = ser('/dev/ttyS0')
        port.baudrate = 115200
        port.open()
        port.flushInput()
        port.timeOut = None
    except:
        print('Unable to open port')
        return
    gps_on(bit=1)
    sleep(10)
    seq = 1
    while seq <= time*60/inter:
        keys = ('GGA', 'GLL', 'GMP', 'GNS', 'GRS', 'GSA', 'GST', 'GSV',
                'HDT', 'RMC', 'ROT', 'VTG', 'ZDA', 'UID', 'ATT')
        is_byte = False
        while not is_byte:
            byte = port.readline()
            print(byte)
            key = 0
            for key, objects in enumerate(keys):
                if byte.find(objects) == -1 and key == 14:
                    # __writeFile('gps_nmea_data.log', byte, 'a')
                    # sleep(2)
                    # is_byte = True
                    break
                elif byte.find(objects) == 3:
                    if byte.find('ATT') != -1:
                        is_byte = True
                    break
                    # print(byte, key, byte.find(objects))
                elif byte.find(objects) == -1:
                    pass
                else:
                    # print(byte)
                    byte = byte[0:int(byte.find(objects))-3]
                    if byte == '$PTP':
                        break
                    __writeFile('gps_nmea_data.log', byte, 'a')
                    sleep(2)
                    is_byte = True
                    break
        sleep(inter)
        seq = seq+1
        print(seq)
    port.close()
    gps_off(bit=1)

# def cover_to_ascii():
#     n = ''
#     with open('gps_binex_data.log', 'rb') as fil:
#         m = fil.readline()
#         # print(m)
#         for b in m:
#             h = bina.b2a_uu(b)[0:-2]
#             # if '\n' in h:
#             #     print('hey')
#             if h != '\n':
#                 n = n+h
#     with open('gps_binex_ascii_data.log.log', 'w') as logg:
#         logg.write(n)
#     print(n)


if __name__ == "__main__":
    with open('gps_binex_data.log', 'wb') as fil:
        fil.write('')
    get_binex(2, 2)
