# Battery, CPU and other ressources monitoring
from time import sleep
import subprocess
from execp import printf


def toggle_1hour():
    """
    set the watchdog to 1hour
    """
    subprocess.call("echo 3 > /sys/class/gpio/wdt_ctl/data", shell=True)
    sleep(2)
    subprocess.call("echo 0 > /sys/class/gpio/wdt_ctl/data", shell=True)
    sleep(2)
    subprocess.call("echo 3 > /sys/class/gpio/wdt_ctl/data", shell=True)


def __toggle_3min():
    """
    set the watchdog to 3min
    """
    # set the power mode
    subprocess.call("echo 1 > /sys/class/gpio/wdt_ctl/data", shell=True)
    sleep(2)
    subprocess.call("echo 0 > /sys/class/gpio/wdt_ctl/data", shell=True)
    sleep(2)
    subprocess.call("echo 1 > /sys/class/gpio/wdt_ctl/data", shell=True)
    printf("Auto watchdog is set to  3 min.")
