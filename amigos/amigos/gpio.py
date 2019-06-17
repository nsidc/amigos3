import subprocess as subprocess
from time import sleep

bit_string = []


def __update_bit(bit):
    with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "w") as power_log:
        power_log.write(bit)


def __toggle(bit):
    """
    Toggle the bit of the index be used
    index 1: Activate power  on GPIO VPROG
    index 0: Activate power on BATLOAD GPIO
    index 2: Activate power on GIO SPARE_E
    """
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/index".format(bit), shell=True)


def router_on(bit):
    """
    Turn the power on router on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = str(power_log.read()).split(",")
            bit_str = bit_string[0][0:6]+"1"+bit_string[0][7:]
        __toggle(bit)
        # print(hex(int(bit_string[0], 2)))
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_str + ','+bit_string[1])


def router_off(bit):
    """
    Turn the power off router off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[0][0:6]+"0"+bit_string[0][7:]
        __toggle(bit)
        sleep(1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_str + ','+bit_string[1])


def gps_on(bit):
    """
    Turn the power on gps module on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[1][0:8]+"1"+bit_string[1][9]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


def gps_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[1][0:8]+"0"+bit_string[1][9:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


def weather_on(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[1][0:6]+"1"+bit_string[1][7:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


def weather_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[1][0:6]+"0"+bit_string[1][7:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


def power_down(bit):
    if bit:
        bit_string = "0b00000000,0b00000000"
        __update_bit(bit_string)
        __toggle(bit-1)
        subprocess.call("echo 0x0> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print("ok\nTitron is going down now!")
        sleep(2)
        subprocess.call("shutdown -h now", shell=True)


def power_up(bit):
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0xFF> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0xFF > /sys/class/gpio/pwr_ctl/data", shell=True)
        print("ok")
        __update_bit('0b11111111,0b11111111')


def CR1000_on(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[1][0:5]+"1"+bit_string[1][6:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


def CR1000_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[1][0:5]+"0"+bit_string[1][6:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        print("ok")
        __update_bit(bit_string[0] + ','+bit_str)


#def dts_on(bit):
#    """
#    Turn the power off gps module on after toggling the bit
#    """
#
#    if bit:
#        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
#            bit_string = power_log.read().split(",")
#            bit_str = bit_string[1][0:5]+"1"+bit_string[1][6:]
#        __toggle(bit-1)
#        subprocess.call(
#            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
#        print("ok")
#        __update_bit(bit_string[0] + ','+bit_str)
#
#
#def dts_off(bit):
#    """
#    Turn the power off gps module on after toggling the bit
#    """
#    if bit:
#        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as power_log:
#            bit_string = power_log.read().split(",")
#            bit_str = bit_string[1][0:5]+"0"+bit_string[1][6:]
#        __toggle(bit-1)
#        subprocess.call(
#            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
#        print("ok")
#        __update_bit(bit_string[0] + ','+bit_str)