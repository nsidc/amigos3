import subprocess as subprocess
from time import sleep


def  __toggle(bit):
    """
    Toggle the bit of the index be used
    index 1: Activate power  on GPIO VPROG
    index 0: Activate power on BATLOAD GPIO
    index 2: Activate power on GIO SPARE_E
    """
    subprocess.call("echo {0} > /sys/class/gpio/pwr_ctl/index".format(bit), shell=True)


def router_on(bit):
    """
    Turn the power on router on after toggling the bit
    """
    if bit:
        __toggle(bit)
        subprocess.call("echo 0x8 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "router is turned on"


def router_off(bit):
    """
    Turn the power off router off after toggling the bit
    """
    if bit:
        __toggle(bit)
        sleep(1)
        subprocess.call("echo 0xF6 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "router is turned off"


def gps_on(bit):
    """
    Turn the power on gps module on after toggling the bit
    """
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0x02 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "gps module is turned on"


def gps_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0xFC > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "gps module is turned off"
