import subprocess as subprocess
from time import sleep
from execp import printf
bit_string = []


def __update_bit(bit):
    with open("/media/mmcblk0p1/logs/power_log.log", "w") as power_log:
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


def modem_on(bit):
    """
    Turn modem module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = str(power_log.read()).split(",")
            bit_str = bit_string[1][0:6]+"1"+bit_string[1][7:]
        __toggle(bit)
        # printf(hex(int(bit_string[0], 2)))
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf('Modern turned on')
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def modem_off(bit):
    """
    Turn modem module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[1][0:6]+"0"+bit_string[1][7:]
        __toggle(bit)
        sleep(1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("Modern turned off")
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def gps_on(bit):
    """
    Turn gps module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[0][0:8]+"1"+bit_string[0][9]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("gps turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def gps_off(bit):
    """
    Turn gps module power off after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[0][0:8]+"0"+bit_string[0][9:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("gps turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def sbd_on(bit):
    """
    Turn weather module power on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:9]+"1"
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("sbd turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def sbd_off(bit):
    """
    Turn weather module power on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:9]+"0"
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("sbd turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def weather_on(bit):
    """
    Turn weather module power on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:6]+"1"+bit_string[0][7:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("Weather station turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def weather_off(bit):
    """
    Turn weather module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:6]+"0"+bit_string[0][7:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("weather station turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def imm_on(bit):
    """
    Turn IMM module power on after toggling the bit
    """

    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:7]+"1"+bit_string[0][8:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("Weather station turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def imm_off(bit):
    """
    Turn IMM module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:7]+"0"+bit_string[0][8:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("weather station turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def power_down(bit):
    if bit:
        bit_string = "0b00000000,0b00000000,0b00000000"
        __update_bit(bit_string)
        __toggle(bit-1)
        subprocess.call("echo 0x0> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(2)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        printf("Tritron is going down now!")
        sleep(2)
        subprocess.call("shutdown -h now", shell=True)


def reboot(bit):
    if bit:
        bit_string = "0b00000000,0b00000000,0b00000000"
        __update_bit(bit_string)
        __toggle(bit-1)
        subprocess.call("echo 0x0> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(2)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        printf("Tritron is going down now for reboot!")
        sleep(2)
        subprocess.call("reboot", shell=True)


def all_off(bit):
    if bit:
        bit_string = "0b00000000,0b00000000,0b00000000"
        __update_bit(bit_string)
        __toggle(bit-1)
        subprocess.call("echo 0x0> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(1)
        __toggle(bit)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(1)
        __toggle(2)
        subprocess.call("echo 0x0 > /sys/class/gpio/pwr_ctl/data", shell=True)
        printf("Turning off all devices now!")


def V5_ENA_ON():
    """
    Enabled 5 volt switch
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:9]+"1"
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("Enabled 5 volt switch")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def V5_ENA_OFF():
    """
    Disabled 5 volt switch
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:9]+"0"
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("Disabled 5 volt switch")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def solar_on():
    """
    Enabled 5 volt to solar sensor
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:6]+"1"+bit_string[2][7:]
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("solar sensor turned on")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def solar_off():
    """
    Disable 5 volt to solar sensor
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:6]+"0"+bit_string[2][7:]
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("solar sensor turned off")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def power_up(bit):
    if bit:
        __toggle(bit-1)
        subprocess.call("echo 0xFF> /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(bit)
        subprocess.call("echo 0xFF > /sys/class/gpio/pwr_ctl/data", shell=True)
        sleep(2)
        __toggle(2)
        subprocess.call("echo 0xFF > /sys/class/gpio/pwr_ctl/data", shell=True)
        printf("All devices powered on")
        __update_bit('0b11111111,0b11111111,0b11111111')


def cr1000_on(bit):
    """
    Turn cr1000 module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:5]+"1"+bit_string[0][6:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("CR1000x turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def cr1000_off(bit):
    """
    Turn cr1000 module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:5]+"0"+bit_string[0][6:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("CR1000x turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def router_on(bit):
    """
    Turn router module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = str(power_log.read()).split(",")
            bit_str = bit_string[1][0:7]+"1"+bit_string[1][8:]
        __toggle(bit)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("router turned on")
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def router_off(bit):
    """
    Turn router module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[1][0:7]+"0"+bit_string[1][8:]
        __toggle(bit)
        sleep(1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("router turned off")
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def iridium_on(bit):
    """
    Turn iridium module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = str(power_log.read()).split(",")
            bit_str = bit_string[1][0:5]+"1"+bit_string[1][6:]
        __toggle(bit)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("iridium  turned on")
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def iridium_off(bit):
    """
    Turn iridium module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(',')
            bit_str = bit_string[1][0:5]+"0"+bit_string[1][6:]
        __toggle(bit)
        sleep(1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("iridium turned off")
        __update_bit(bit_string[0] + ','+bit_str+','+bit_string[2])


def dts_on(bit):
    """
    Turn windows/dts module power on after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:3]+"1"+bit_string[0][4:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("dts turned on")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def dts_off(bit):
    """
    Turn windows/dts module power off after toggling the bit
    """
    if bit:
        with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
            bit_string = power_log.read().split(",")
            bit_str = bit_string[0][0:3]+"0"+bit_string[0][4:]
        __toggle(bit-1)
        subprocess.call(
            "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
        printf("dts turned off")
        __update_bit(bit_str + ','+bit_string[1]+','+bit_string[2])


def enable_serial():
    """
    Enable serial communication
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:8]+"1"+bit_string[2][9:]
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("serial communication enable")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def disable_serial():
    """
    Enable serial communication
    """
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power_log:
        bit_string = power_log.read().split(',')
        bit_str = bit_string[2][0:8]+"0"+bit_string[2][9:]
    __toggle(2)
    sleep(1)
    subprocess.call(
        "echo {0} > /sys/class/gpio/pwr_ctl/data".format(hex(int(bit_str, 2))), shell=True)
    printf("serial communication disable")
    __update_bit(bit_string[0] + ','+bit_string[1]+','+bit_str)


def is_on_checker(bit_index, bit_number):
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as logfile:
        bits = logfile.read().split(",")
        return int(bits[bit_index][bit_number])
