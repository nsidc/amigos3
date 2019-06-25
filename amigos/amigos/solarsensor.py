import math
import time
from time import sleep
import sys
import os
import csv
import binascii

from datetime import datetime
import subprocess


def readsolar():
    solar1 = open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp1.txt", "w+")
    solar1.close()
    # To read the battery voltage analog input:

    solar2 = open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp2.txt", "w+")
    solar2.close()
    t = 0
    data = 0
    # take voltage readings at a specific rate for a specified amount of time
    while t <= 30:  # how long to take readings for (seconds)
        subprocess.call("echo 0 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
        sleep(1)
        subprocess.call('cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/amigos/amigos/logs/solar_temp1.txt', shell=True)

        subprocess.call("echo 1 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
        sleep(1)
        subprocess.call('cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/amigos/amigos/logs/solar_temp2.txt', shell=True)

        with open('/media/mmcblk0p1/amigos/amigos/logs/solar_temp1.txt', "r") as solar_temp1:
            data1 = solar_temp1.read()
            data1 = int(data1, 16)
            #print(data1)
        with open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp2.txt", "r") as solar_temp2:
            data2 = solar_temp2.read()
            data2 = int(data2, 16)
            #print(data2)
        data = data1/data2
        data = str(data)
        #print(data)
        with open("/media/mmcblk0p1/amigos/amigos/logs/solar_data.txt", "a+") as solar:
            solar.write(data + '\n')
            sleep(8)  # set rate of readings in seconds
        t = t + 10  # keep time
        # print(t)

# average data every min
if __name__ == "__main__":
    readsolar()