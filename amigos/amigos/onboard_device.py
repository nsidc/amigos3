import subprocess as subprocess
from time import sleep
import datetime


def get_humidity():
    data = 0
    date = str(datetime.datetime.now())
    subprocess.call(
        'cat /sys/class/hwmon/hwmon0/device/humidity1_input > /media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', shell=True)
    sleep(1)
    with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', 'r') as temp:
        data = float(temp.read())/1000
    with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_humid.log', 'a+') as humid:
        humid.write(date + '\n' + str(data)+'\n')
    sleep(2)
    subprocess.call(
        'rm /media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', shell=True)


def get_temperature():
    data = 0
    date = str(datetime.datetime.now())
    subprocess.call(
        'cat /sys/class/hwmon/hwmon0/device/temp1_input> /media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', shell=True)
    sleep(1)
    with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', 'r') as temp:
        data = float(temp.read())/1000
    with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_temperature.log', 'a+') as temp:
        temp.write(date + '\n' + str(data)+'\n')
    sleep(2)
    subprocess.call(
        'rm /media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', shell=True)


if __name__ == "__main__":
    get_humidity()
    get_temperature()
