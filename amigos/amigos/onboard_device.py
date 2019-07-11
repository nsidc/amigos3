import subprocess as subprocess
from time import sleep
import datetime
from execp import printf
from subprocess import Popen, PIPE, call
import traceback


def get_humidity():
    data = 0
    try:
        date = str(datetime.datetime.now())
        call(
            'cat /sys/class/hwmon/hwmon0/device/humidity1_input > /media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', shell=True)
        sleep(1)
        with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', 'r') as temp:
            data = float(temp.read())/1000
        with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_humid.log', 'a+') as humid:
            humid.write(date + '\n' + str(data)+'\n')
        sleep(2)
        call(
            'rm /media/mmcblk0p1/amigos/amigos/logs/onboard_humid_temp.log', shell=True)
    except:
        printf('Failed to acquire on board humidity')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))


def get_temperature():
    data = 0
    try:
        date = str(datetime.datetime.now())
        subprocess.call(
            'cat /sys/class/hwmon/hwmon0/device/temp1_input> /media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', shell=True)
        sleep(1)
        with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', 'r') as temp:
            data = float(temp.read())/1000
        with open('/media/mmcblk0p1/amigos/amigos/logs/onboard_temperature.log', 'a+') as temp:
            temp.write(date + '\n' + str(data)+'\n')
        sleep(2)
        call(
            'rm /media/mmcblk0p1/amigos/amigos/logs/onboard_temperature_temp.log', shell=True)
    except Exception as err:
        printf('Failed to acquire on board temperature')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))


def get_battery_voltage():
    try:  # get the voltage of the battery
        Vref_10 = 33
        Vdividor = 4095
        Vmultiplier = 7997
        Vfinal_dividor = 10000
        call('echo 4 > /sys/class/gpio/mcp3208-gpio/index', shell=True)
        sleep(1)
        p = Popen("cat /sys/class/gpio/mcp3208-gpio/data",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out = p.communicate()
        volt = (((float(int('0x'+out[0], 16))*Vref_10)/Vdividor)*Vmultiplier)/Vfinal_dividor
        return volt
    except:
        printf('Failed to acquire board input voltage')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))


def get_battery_current():
    try:  # get the current of the battery
        dividor=4095
        # was 829 org
        multiplier=790
        final_dividor=100
        call('echo 5 > /sys/class/gpio/mcp3208-gpio/index', shell=True)
        sleep(1)
        p=Popen("cat /sys/class/gpio/mcp3208-gpio/data",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out=p.communicate()
        curr=(float(int('0x'+out[0], 16))*multiplier/dividor)/final_dividor
        return curr
    except:
        printf('Failed to acquire board input current')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))


if __name__ == "__main__":
    get_humidity()
    get_temperature()
