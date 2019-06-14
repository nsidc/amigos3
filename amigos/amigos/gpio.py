import subprocess as subprocess
from time import sleep


flag = {"weather": 0, "gps": 0, "cr1000": 0, "router": 0}
bit_string = "0b00000000,0b0000000"

with open("/logs/power_log.txt", "w") as power_log:
    power_log.write(bit_string)


def __update_bit(bit):
    with open("/logs/power_log.txt", "w") as power_log:
        power_log.write(bit_string)


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
    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split(",")
    bit_string[0] = bit_string[0][0:5]+"1"+bit_string[0][7:]
    if bit:
        __toggle(bit)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(bit_string[0]), shell=True)
        print("router is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])


def router_off(bit):
    """
    Turn the power off router off after toggling the bit
    """

    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split()
    bit_string[0] = bit_string[0][0:5]+"0"+bit_string[0][7:]
    if bit:
        __toggle(bit)
        sleep(1)
        subprocess.call(
            "echo {} > /sys/class/gpio/pwr_ctl/data".format(bit_string[0]), shell=True)
        print("router is turned off")
    __update_bit(bit_string[0] + ','+bit_string[1])


def gps_on(bit):
    """
    Turn the power on gps module on after toggling the bit
    """

    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split()
    bit_string[1] = bit_string[1][0:7]+"1"+bit_string[1][9]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} > /sys/class/gpio/pwr_ctl/data".format(bit_string[1]), shell=True)
        print("gps module is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])


def gps_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split()
    bit_string = bit_string[1][0:7]+"0"+bit_string[1][9]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} > /sys/class/gpio/pwr_ctl/data".format(bit_string[1]), shell=True)
        print("gps module is turned off")
    __update_bit(bit_string[0] + ','+bit_string[1])


def weather_on(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split(",")
    bit_string[1] = bit_string[1][0:5]+"1"+bit_string[1][7:]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} /sys/class/gpio/pwr_ctl/data".format(bit_string), shell=True)
        print("weather module is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])


def weather_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """
    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split(",")
    bit_string[1] = bit_string[1][0:5]+"0"+bit_string[1][7:]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} /sys/class/gpio/pwr_ctl/data".format(bit_string), shell=True)
        print("weather module is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])


def power_down(bit):
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0x0> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        print("Power is down on peripherals\nTitron is going down!")
        sleep(2)
        subprocess.call("shutdown -h now", shell=True)


def power_up(bit):
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0xFF> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0xFF > /sys/class/gpio/pwr_ctl/data", shell=True)
        print("Power is up on peripherals")
    __update_bit('0b11111111,1b11111111')


def CR1000_on(bit):
    """
    Turn the power off gps module on after toggling the bit
    """

    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split(",")
    bit_string[1] = bit_string[1][0:5]+"1"+bit_string[1][7:]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} /sys/class/gpio/pwr_ctl/data".format(bit_string), shell=True)
        print("weather module is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])


def CR1000_off(bit):
    """
    Turn the power off gps module on after toggling the bit
    """
    with open("/logs/power_log.txt", "w") as power_log:
        bit_string = power_log.read().split(",")
    bit_string[1] = bit_string[1][0:5]+"0"+bit_string[1][7:]
    if bit:
        __toggle(bit-1)
        subprocess.call(
            "echo {} /sys/class/gpio/pwr_ctl/data".format(bit_string), shell=True)
        print("weather module is turned on")
    __update_bit(bit_string[0] + ','+bit_string[1])