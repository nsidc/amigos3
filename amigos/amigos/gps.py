# !/bin/python2
import pynmea2 as nmea2
from serial import Serial as ser
from time import sleep
# import binascii as bina
from gpio import gps_off, gps_on, enable_serial, disable_serial


def writeFile(file_name, strings, form):
    """
    Create or write to an existing file
    File_name: string representations of the file name
    String: the string to be writing to the file
    form: a,w, ... the format of the file to be open.
    Return: true when done
    """
    with open(file_name, form) as fil:
        fil.write(strings)
        # print('Writing data')
    return True


class gps_data():
    def __init__(self, *args, **kwargs):
        self.cmd = {
            'binex': 'out,,binex/',
            'nmea': 'out,,nmea/',
            'GPGGA': 'out,,nmea/',
            'GPVTG': 'out,,nmea/'
        }
        self.sequence = 1
        self.is_saved = False
        self.interval = 15
        self.timeout = 10

    def get_binex(self):
        """
        Initiate the reading of the binex language from GPS module to Titron
        Take no argument
        Return None
        """
        try:
            # try opening the port
            self.port.open()
            enable_serial()
            gps_on(bit=1)
            sleep(60)
            self.port.flusInput()
        except:
            self.port = None
            print('Unable to open port')
        else:
            while self.sequence <= self.timeout*60/self.interval:
                self.port.write(self.cmd['binex'])
                sleep(2)
                data = self.port.read(self.port.inWaiting())
                writeFile(
                    '/media/mmcblk0p1/amigos/amigos/logs/gps_binex_data.txt', data, 'a')
                sleep(self.interval)
                self.sequence = self.sequence+1
        finally:
            # At every exit close the port, and turn off the GPS
            if self.port:
                self.port.close()
            gps_off(bit=1)
            disable_serial()

    def get_nmea(self):
        """
        Initiate the reading of the binex language from GPS module to Titron
        Take no argument
        Return Nonem
        """
        try:
            # try opening the port
            self.port.open()
            enable_serial()
            gps_on(bit=1)
            sleep(60)
            self.port.flusInput()
        except:
            self.port = None
            print('Unable to open port')
        else:
            while self.sequence <= self.timeout*60/self.interval:
                self.port.write(self.cmd['nmea'])
                sleep(2)
                data = self.port.read(self.port.inWaiting())
                writeFile('/media/mmcblk0p1/amigos/amigos/logs/gps_nmea_data.txt', data, 'a')
                sleep(self.interval)
                self.sequence = self.sequence+1
        finally:
            # At every exit close the port, and turn off the GPS
            if self.port:
                self.port.close()
            gps_off(bit=1)
            disable_serial()

    def __get_GPGGA_GPVTG(self):
        try:
            # try opening the port
            self.port.open()
            enable_serial()
            gps_on(bit=1)
            sleep(30)
            self.port.flusInput()
        except:
            self.port = None
            print('Unable to open port')
        else:
            self.port.write(self.cmd['GPGGA'])
            sleep(1)
            GPGGA = self.port.readline()
            self.port.write(self.cmd['GPVTG'])
            sleep(1)
            GPVTG = self.port.readline()
            return GPGGA, GPVTG
        finally:
            # At every exit close the port, and turn off the GPS
            if self.port:
                self.port.close()
            gps_off(bit=1)
            disable_serial()

    def __Nmea_parse(self):
        """
        Parser the nmea language code into human readable location code GPGGA, GPVTG
        Take no argument
        Return  GPGGA_parser, GPVTG_parser
        """
        GPGGA, GPVTG = self.__get_GPGGA_GPVTG()  # get the rwa data
        GPGGA_parser = None
        GPVTG_parser = None
        if GPGGA and GPVTG:
            GPGGA_parser = nmea2.parse(GPGGA)  # parser the data
            GPVTG_parser = nmea2.parse(GPVTG)
        # print(GPGGA_parser, GPVTG_parser)
        return GPGGA_parser, GPVTG_parser

    def quick_gps_data(self):
        """
        Output the location of the amigos module with less precision
        take no argument
        Return nothing
        """
        gps_data = self.__Nmea_parse()
        # print(gps_data)  # call the parser function to get location
        Altitude = gps_data[0].altitude  # retrieve altitude
        Longitude = gps_data[0].lon  # retrive longitude
        Longitude_Dir = gps_data[0].lon_dir  # retrive longitude direction
        Latitude = gps_data[0].lat  # retrive latitude
        Latitude_Dir = gps_data[0].lat_dir
        # retrive latitude direction
        spd_over_grnd = gps_data[1].spd_over_grnd_kmph
        sat = gps_data[0].num_sats
        print(" Altitude: {0} m\n Longitude: {1} m\n Longitude Dir: {2}\n Latitude:{3}m\n Latitude Dir: {4}\n spd_over_grnd: {6} Kmph\n Total Satellites: {5}".format(
            Altitude, Longitude, Longitude_Dir, Latitude, Latitude_Dir, sat, spd_over_grnd))

if __name__ == "__main__":
    bn = gps_data()
    bn.timeout = 2
    bn.interval = 2
    bn.quick_gps_data()
