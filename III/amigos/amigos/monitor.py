# Battery, CPU and other ressources monitoring
import os
from time import sleep


def watchdog(value=1):
    """
    Set the watchdog update interval
    """
    if value == 1:
        os.system('echo 1 > /sys/class/gpio/wdt_ctl/data')
        sleep(1)
        os.system('echo 0 > /sys/class/gpio/wdt_ctl/data')
    else:
        os.system('echo 1 > /sys/class/gpio/wdt_ctl/data')
        sleep(1)
        os.system('echo 1 > /sys/class/gpio/wdt_ctl/data')


def power(value=1):
    """
    Turn power off and on power from peripheral
    """
    if value == "internet":
        os.system('echo 1 > /sys/class/gpio/pwr_ctl/index')
        sleep(1)
        os.system('echo 0x80 > /sys/class/gpio/pwr_ctl/data')
