import subprocess as subprocess
from time import sleep


def toggle(bit):

    subprocess.call("echo {0} > /sys/class/gpio/pwr_ctl/index".format(bit), shell=True)
    print bit


def router_on(bit):
    if bit:
        toggle(bit)
        subprocess.call("echo 0x8 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "router is turned on"
        print bit


def router_off(bit):
    if bit:
        toggle(bit)
        sleep(1)
        subprocess.call("echo 0xF6 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "router is turned off"
        print bit


def gps_on(bit):
    if bit:
        toggle(bit-1)
        subprocess.call("echo 0x02 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "gps module is turned on"
        print bit


def gps_off(bit):
    if bit:
        toggle(bit-1)
        subprocess.call("echo 0xFC > /sys/class/gpio/pwr_ctl/data", shell=True)
        print "gps module is turned off"
        print bit
