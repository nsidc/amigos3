
from time import sleep
import subprocess as subprocess
import datetime


def readsolar():
    solar1 = open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp1.log", "w+")
    solar1.close()
    # To read the battery voltage analog input:

    solar2 = open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp2.log", "w+")
    solar2.close()
    t = 0
    data = 0
    # take voltage readings at a specific rate for a specified amount of time
    while t <= 30:  # how long to take readings for (seconds)
        subprocess.call("echo 0 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
        sleep(1)
        subprocess.call(
            'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/amigos/amigos/logs/solar_temp1.log', shell=True)

        subprocess.call("echo 1 > /sys/class/gpio/mcp3208-gpio/index", shell=True)
        sleep(1)
        subprocess.call(
            'cat /sys/class/gpio/mcp3208-gpio/data > /media/mmcblk0p1/amigos/amigos/logs/solar_temp2.log', shell=True)

        with open('/media/mmcblk0p1/amigos/amigos/logs/solar_temp1.log', "r") as solar_temp1:
            data1 = solar_temp1.read()
            data1 = int(data1, 16)
            # print(data1)
        with open("/media/mmcblk0p1/amigos/amigos/logs/solar_temp2.log", "r") as solar_temp2:
            data2 = solar_temp2.read()
            data2 = int(data2, 16)
            # print(data2)
            date = str(datetime.datetime.now())
            data = date + "  " + str(data1) + "  " + str(data2) + "\n"
        data = str(data)
        # print(data)
        with open("/media/mmcblk0p1/amigos/amigos/logs/solar_data.log", "a+") as solar:
            solar.write(data + '\n')
            sleep(8)  # set rate of readings in seconds
        t = t + 10  # keep time
        # print(t)
    subprocess.call(
        'rm /media/mmcblk0p1/amigos/amigos/logs/solar_temp1.log', shell=True)
    subprocess.call(
        'rm /media/mmcblk0p1/amigos/amigos/logs/solar_temp2.log', shell=True)


# average data every min
if __name__ == "__main__":
    readsolar()
