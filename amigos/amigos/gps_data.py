# !/bin/python2
import pynmea2 as nmea2
from serial import Serial as ser
from time import sleep
# import binascii as bina
from gpio import gps_off, gps_on
from radium import read, send


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


class binex():
    """
    Get binex data from GPS module and save it as a binary file.
    is_saved: if the read line has been saved to the log file
    interval: interval or frequency to acquire data
    timeOut: How long to acquire data during each interval
    """

    def __init__(self, *args, **kwargs):
        self.sequence = 1
        self.is_saved = False
        self.interval = 15
        self.timeout = 15
        try:
            self.port = ser('/dev/ttyS0')  # set the port
            self.port.baudrate = 115200  # set baudrate
            self.port.timeOut = None  # set port time out
        except:
            self.port = None
            print('Unable to setup port')

    def __binex_proce(self, byte, keys, is_byte):
        """
        Process the binex file and saved it to the log file
        byte: the read binex string (in binary)
        keys: the nmea keys
        is_byte: is set  when all binex is written to file
        """
        key = 0
        for key, objects in enumerate(keys):  # loop through the keys
            # check if object is present in the byte data read
            if byte.find(objects) != 3:
                # in case no objects is found till the end of the loop
                if byte.find(objects) == -1 and key == 14 and byte.find("\r\n") == -1:
                    # check the byte for empty string or end of line
                    if byte != '\n' or byte != '':
                        self.is_saved = writeFile(
                            'gps_binex_data.log', byte, 'ab')
                        sleep(2)
                        break
                # object found a position 3 do nothing (no a binex)
                elif byte.find(objects) == 3:
                    break
                # object not found, keep looping till all the end of the keys array
                elif byte.find(objects) == -1:
                    pass
                # The binex and the nmea are attached, here we separate them
                else:
                    # separate the binex
                    bytes = byte[0:int(byte.find(objects))-3]
                    # it could happen that the last string is just ATT or $PTP
                    if bytes == '$PTP' or byte.find('ATT') != -1:
                        break
                    # write the cut byte to the file
                    elif bytes or bytes != '\n':
                        # print(3, bytes)
                        self.is_saved = writeFile(
                            'gps_binex_data.log', bytes, 'ab')
                        sleep(2)
                        is_byte = True
                        break
            # Check if that is saved and the byte has GGA in it
            if self.is_saved == True and byte.find('GGA') != -1:
                is_byte = True  # All the binex has been written to file
                self.sequence = self.sequence+1  # increment sequence
                print(self.sequence)
                self.is_saved = False  # reset the variable is_saved
                sleep(self.interval)  # wait for interval
                break
        return is_byte  # return that All the binex has been written to file

    def get_binex(self):
        """
        Initiate the reading of the binex language from GPS module to Titron
        Take no argument
        Return None
        """
        try:
            # try opening the port
            self.port.open()
        except:
            self.port = None
            print('Unable to open port')
        else:
            # turn the GPS module on
            gps_on(bit=1)
            # Wait for 40 s for GPS module to set up
            # It was notice that if the wait is not long enough, the data received from the module are incomplete
            sleep(40)
            # set the sequence: how many junk of reading has to be taken
            while self.sequence <= self.timeout*60/self.interval:
                # flush the port to delete very data before reading, so we get fresh reading
                self.port.flushInput()
                # This are the kys persent in all nmea reading
                keys = ('GGA', 'GLL', 'GMP', 'GNS', 'GRS', 'GSA', 'GST', 'GSV',
                        'HDT', 'RMC', 'ROT', 'VTG', 'ZDA', 'UID', 'ATT')
                # No binex has been saved to set the is_byte to false
                is_byte = False
                while not is_byte:
                    # Read  a line of string from the port
                    byte = self.port.readline()
                    # Process the reading and save it to the log file
                    is_byte = self.__binex_proce(byte, keys, is_byte)

        finally:
            # At every exit close the port, and turn off the GPS
            if self.port:
                self.port.close()
            gps_off(bit=1)


class nmea():
    """
    Get NMEA data from GPS module and save it as a binary file.
    is_done: Check wether all lines has been saved for the sequence
    interval: interval or frequency to acquire data
    timeOut: How long to acquire data during each interval
    """

    def __init__(self, *args, **kwargs):

        self.sequence = 1
        self.done = False
        self.interval = 15
        self.timeout = 15
        try:
            self.port = ser('/dev/ttyS0')  # set the port
            self.port.baudrate = 115200  # set baudrate
            self.port.timeOut = None  # set port time out
            self.port.flushInput()
        except:
            self.port = None
            print('Unable to setup port')

    def __get_GPGGA_GPVTG(self):
        """
        Read raw data in nmea format from the GPS module. The GPGGA, GPVTG only
        Take not argument
        Return the GPGGA, GPVTG variable
        """
        try:
            # try opening the port
            self.port.open()
        except:
            self.port = None
            print('Unable to open port')
        else:
            # set GPGGA, GPVTG to None
            gps_on(1)
            print('Waiting for 5 minute. GPS module not fully started!')
            sleep(120)
            self.port.flushInput()
            GPVTG = None
            GPGGA = None
            # loop and find the GPGGA, GPVTG variable
            while GPGGA is None or GPVTG is None:
                data = self.port.readline()
                try:
                    if data.find('VTG') != -1:
                        # print(data)
                        GPVTG = data
                    elif data.find('GPGGA') == 1:
                        GPGGA = data
                except:
                    print("Unable to read. Check GPS module configuration or try again")
                    return 0, 0
        finally:
            # Close port and turn off GPS module
            if self.port:
                self.port.close()
                gps_off(1)

        sleep(1)
        return GPGGA, GPVTG

    def __get_all(self):
        """
        Get all the NMEA data from the GPS module
        Take no argument
        Return None
        """
        # NMEA language keys
        keys = ('GGA', 'GLL', 'GMP', 'GNS', 'GRS', 'GSA', 'GST', 'GSV',
                       'HDT', 'RMC', 'ROT', 'VTG', 'ZDA', 'UID', 'PSR')
        self.done = False
        while not self.done:  # loop till all keys are saved
            byte = self.port.readline()  # read a line from the port
            key = 0
            for key, objects in enumerate(keys):
                if byte.find('PSR') == 3:  # Check for tge last key in at the port
                    self.done = True
                if byte.find(objects) != -1:  # if the key is found is the string
                    # the key is not at the begining of the string then NMEA and BINEX are attached
                    if byte.find(objects) != 3:
                        # separate NMEA from BINEX and save the string
                        bytes = byte[int(byte.find(objects))-3:]
                        writeFile('gps_nmea_data.log', bytes, 'a')
                        sleep(.3)
                        break

                    elif byte.find(objects) == 3:  # Key at the bigging then save the string
                        writeFile('gps_nmea_data.log', byte, 'a')
                        sleep(.3)
                        break
                else:
                    pass
        self.sequence = self.sequence+1  # increment sequence
        writeFile('gps_nmea_data.log', '-'*50 + '\n', 'a')  # write a delimiter

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

    def get_nmea(self):
        """
        Get the nmea language from gps module and save it to file.
        Take no argument
        Return None
        """
        try:
            # Try to open the port
            self.port.open()
        except:
            self.port = None
            print('Unable to open port')
        else:
            gps_on(bit=1)  # turn GPS on
            sleep(40)  # wait for 40 s for module to fully start
            # start reading
            while self.sequence <= self.timeout*60/self.interval:
                self.port.flushInput()
                self.__get_all()
                sleep(self.interval)  # wait for the interval

        finally:
            # close port and turn gps module off
            if self.port:
                self.port.close()
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
    bn = nmea()
    bn.timeout = 2
    bn.interval = 2
    bn.quick_gps_data()
