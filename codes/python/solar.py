
from time import sleep
import subprocess
import datetime
from gpio import solar_off, solar_on, is_on_checker
import traceback
from execp import printf


def readsolar():
    solar_on()
    sleep(5)
    solar1 = open("/media/mmcblk0p1/logs/solar_temp1.log", "w+")
    solar1.close()
    # To read the battery voltage analog input:

    solar2 = open("/media/mmcblk0p1/logs/solar_temp2.log", "w+")
    solar2.close()
    t = 0
    data = 0
    # take voltage readings at a specific rate for a specified amount of time
    try:
        while t <= 30:  # how long to take readings for (seconds)
            subprocess.call("echo 0 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
            sleep(1)
            subprocess.call(
                'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/logs/solar_temp1.log', shell=True)

            subprocess.call("echo 1 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
            sleep(1)
            subprocess.call(
                'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/logs/solar_temp2.log', shell=True)

            with open('/media/mmcblk0p1/logs/solar_temp1.log', "r") as solar_temp1:
                data1 = solar_temp1.read()
                data1 = int(data1, 16)
                # print(data1)
            with open("/media/mmcblk0p1/logs/solar_temp2.log", "r") as solar_temp2:
                data2 = solar_temp2.read()
                data2 = int(data2, 16)
                # print(data2)
                date = str(datetime.datetime.now())
                data = date + ",  " + str(data1) + ",  " + str(data2) + "\n"
            data = str(data)
            # print(data)
            with open("/media/mmcblk0p1/logs/solar.log", "a+") as solar:
                solar.write(data + '\n')
                sleep(8)  # set rate of readings in seconds
            t = t + 10  # keep time
    except:
        printf("Unable to read solar sensor")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        # print(t)
    finally:
        solar_off()
        subprocess.call(
            'rm /media/mmcblk0p1/logs/solar_temp1.log', shell=True)
        subprocess.call(
            'rm /media/mmcblk0p1/logs/solar_temp2.log', shell=True)
    


class solar_live():
    def read_solar(self):
        try:
            is_on = is_on_checker(2, 6)
            if not is_on:
                # Turn on Weather Station
                solar_on()
                sleep(5)
        except:
            print("Problem with turning on solar sensor")
        else:
            solar1 = open("/media/mmcblk0p1/logs/solar_temp1.log", "w+")
            solar1.close()
            solar2 = open("/media/mmcblk0p1/logs/solar_temp2.log", "w+")
            solar2.close()

            subprocess.call("echo 0 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
            sleep(1)
            subprocess.call(
                'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/logs/solar_temp1.log', shell=True)

            subprocess.call("echo 1 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
            sleep(1)
            subprocess.call(
                'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/logs/solar_temp2.log', shell=True)

            with open('/media/mmcblk0p1/logs/solar_temp1.log', "r") as solar_temp1:
                data1 = solar_temp1.read()
                data1 = int(data1, 16)
            with open("/media/mmcblk0p1/logs/solar_temp2.log", "r") as solar_temp2:
                data2 = solar_temp2.read()
                data2 = int(data2, 16)
        finally:
            if not is_on:
                solar_off()

        return data1, data2

    def solar_sbd(self):
        data1, data2 = self.read_solar()
        array = [data1,data2]
        solar_dict = {
            'S1':array[0],
            'S2':array[1]
        }
        return str(solar_dict)


    def solar_1(self):
        data1, data2 = self.read_solar()
        data = 0
        date = str(datetime.datetime.now())
        data = date + ",  " + str(data1) + "\n"
        data = str(data)
        print(data)

    def solar_2(self):
        data1, data2 = self.read_solar()
        data = 0
        date = str(datetime.datetime.now())
        data = date + ",  " + str(data2) + "\n"
        data = str(data)
        print(data)

    def solar_all(self):
        data1, data2 = self.read_solar()
        data = 0
        date = str(datetime.datetime.now())
        data = date + ",  " + str(data1) + ",  " + str(data2) + "\n"
        data = str(data)
        print(data)


# average data every min
if __name__ == "__main__":
    readsolar()
