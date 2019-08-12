# !/bin/python2
from serial import Serial as ser
from time import sleep
# import binascii as bina
from gpio import gps_off, gps_on, enable_serial, disable_serial
import subprocess
from execp import printf
from monitor import reschedule
import traceback
import datetime
import os


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
            # Binex command accepted by GPS
            'binex': 'out,,binex/{00_00,01_01,01_02,01_05,01_06,7E_00,7D_00,7F_02,7F_03,7F_04,7F_05}',
            # Nmea Command accepted by GPS
            'nmea': 'out,,nmea/{GGA,GLL,GMP,GNS,GRS,GSA,GST,GSV,HDT,RMC,ROT,VTG,ZDA,UID,P_ATT}',
            'GPGGA': 'out,,nmea/GGA',
            'GPVTG': 'out,,nmea/VTG'
        }
        self.sequence = 1
        self.is_saved = False
        self.interval = 15
        self.timeout = 10
        try:
            self.port = ser('/dev/ttyS0')  # set the port
            self.port.baudrate = 115200  # set baudrate
            self.port.timeOut = None  # set port time out
        except:
            self.port = None
            printf('Unable to setup port ``\\_(^/)_/``')

    # @catch_exceptions(cancel_on_failure=True)
    def get_gpstime(self):
        """Get time from GPS Unit

        Returns:
            String -- Time from gps in YYYY-MM-DD HH:MM:SS format
        """
        self.port.flushInput()
        self.port.write("print,/par/time/utc/date\r\n")
        sleep(2)
        raw_date = self.port.read(self.port.inWaiting()).split(" ")[1].split("\r")[0]
        self.port.write("print,/par/time/utc/clock\r\n")
        sleep(2)
        raw_clock = self.port.read(self.port.inWaiting()).split(" ")[1].split(".")[0]
        gps_time = raw_date + " " + raw_clock
        return gps_time

    def update(self, str_time, date_now):
        """Update the time on tritron

        Arguments:
            str_time {string} -- New time
            date_now {String} -- Old time
        """
        # subprocess.call(
        #     'bash /media/mmcblk0p1/codes/bash/set_time "{0}"'.format(str_time), shell=True)
        os.system('date -s "{0}" > /dev/null'.format(str_time))
        sleep(2)
        date_af = datetime.datetime.now()
        printf("Time updated. Before: {0}; After: {1}".format(date_now, date_af))
        print ("Before: {0}; After: {1}".format(date_now, date_af))

    def update_time(self, out=False):
        """Check for time update
        """
        if out:
            enable_serial()
            gps_on(1)
            sleep(30)
        try:
            str_time = self.get_gpstime()
            date_now = datetime.datetime.now()
            date_time_obj = datetime.datetime.strptime(
                str_time, '%Y-%m-%d %H:%M:%S')
            diff = str(date_time_obj-date_now)
            diff_split = diff.split(":")
            if diff.find("-") != -1:
                diff = str(date_now-date_time_obj)
                diff_split = diff.split(":")
                if diff.find("day") != -1:
                    self.update(str_time, date_now)
            elif int(diff_split[-2]) > 1 or int(diff_split[-3]) > 0:
                self.update(str_time, date_now)
            else:
                print("Time difference is less than 2 minutes. No time update need it")
                printf("Time difference is less than 2 minutes. No time update need it")
                return
        finally:
            if out:
                gps_off(1)
                disable_serial()
                out=False
        # subprocess.call(
        #     'bash /media/mmcblk0p1/codes/bash/set_time "{0}"'.format(str_time), shell=True)
        # os.system('date -s "{0}" >/dev/null'.format(str_time))
        # sleep(2)
        # date_af = datetime.datetime.now()
        # printf("Time updated. Before: {0}; After: {1}".format(date_now, date_af))
        # print ("Before: {0}; After: {1}".format(date_now, date_af))

    def get_binex(self):
        """
        Initiate the reading of the binex language from GPS module to Titron
        Take no argument
        Return None
        """
        printf('GPS data acquisition started')
        try:
            # try opening the port
            self.port.open()
            enable_serial()
            gps_on(bit=1)
            sleep(60)
        except:
            set_reschedule("get_binex")
            self.port = None
            printf('An error occurred ``\\_(^/)_/``')
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            reschedule(re="get_binex")

        else:
            self.port.flushInput()
            self.sequence = 1
            while self.sequence <= self.timeout*60/self.interval:
                self.port.write(self.cmd['binex']+'\r')
                sleep(2)
                data = self.port.read(self.port.inWaiting())
                writeFile(
                    '/media/mmcblk0p1/logs/gps_binex_temp.log', data, 'w+')
                try:
                    subprocess.call(
                        "cat /media/mmcblk0p1/logs/gps_binex_temp.log >> /media/mmcblk0p1/logs/gps_binex.log", shell=True)
                except:
                    writeFile(
                        '/media/mmcblk0p1/logs/gps_binex.log', '', 'a+')
                    subprocess.call(
                        "cat /media/mmcblk0p1/logs/gps_binex_temp.log >> /media/mmcblk0p1/logs/gps_binex.log", shell=True)
                    printf("An error occurred during file dumping ``\\_(^/)_/``")
                    traceback.print_exc(
                        file=open("/media/mmcblk0p1/logs/system.log", "a+"))
                sleep(2)
                if self.port.inWaiting() != 0:
                    data = self.port.read(self.port.inWaiting())
                    writeFile(
                        '/media/mmcblk0p1/logs/gps_binex_temp.log', data, 'w+')
                    sleep(1)
                    subprocess.call(
                        "cat /media/mmcblk0p1/logs/gps_binex_temp.log >> /media/mmcblk0p1/logs/gps_binex.log", shell=True)
                sleep(self.interval-5)
                self.sequence = self.sequence+1
            printf("Updating Tritron time")
            self.update_time()
            printf("All done with gps")
            reschedule(run="get_binex")
        finally:
            # At every exit close the port, and turn off the GPS
            if self.port:
                self.port.close()
            subprocess.call(
                "rm /media/mmcblk0p1/logs/gps_binex_temp.log", shell=True)
            gps_off(bit=1)
            disable_serial()

    def get_nmea(self):
        """Initiate the reading of the binex language from GPS module to Titron

        Returns:
            None -- [description]
        """
        try:
            # try opening the port
            self.port.open()
            enable_serial()
            gps_on(bit=1)
            sleep(90)
            self.port.flusInput()
        except:
            self.port = None
            printf('An error occurred ``\\_(^/)_/``')
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        else:
            self.port.write(self.cmd['nmea'] + "\r")
            sleep(2)
            data = self.port.read(self.port.inWaiting())
            writeFile(
                '/media/mmcblk0p1/logs/gps_nmea.log', data, 'a+')
            sleep(2)
            return data.split("\n")
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
            printf('Unable to open port ``\\_(^/)_/``')
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
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
        import pynmea2 as nmea2
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
