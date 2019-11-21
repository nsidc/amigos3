from collections import namedtuple
import logging
import os

# --------------------------------------------------------------------------------
# GENERAL CONFIGURATION
# --------------------------------------------------------------------------------

_MODES = ('SAFE', 'TEST', 'NORMAL', 'WINTER', 'SUMMER')
MODES = namedtuple('MODES', _MODES)(*_MODES)

DEFAULT_MODE = MODES.NORMAL
MODE = getattr(MODES, os.environ.get('MODE', DEFAULT_MODE))

LOG_DIR = '/media/media/mmcblk0p1/logs'
LOG_FILENAME = 'system.log'
LOG_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
DEFAULT_LOG_LEVEL = 'INFO'
LOG_LEVEL = getattr(logging, os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL))
LOG_SIZE = 200000

# --------------------------------------------------------------------------------
# UNIT SPECIFIC CONFIGURATION
# --------------------------------------------------------------------------------

_UNIT = namedtuple(
    'UNIT', ('NAME', 'MAC_ADDRESS', 'SEABIRD_IDS', 'AQUADOPP_IDS', 'DATA_DIR')
)


UNITS = namedtuple('UNITS', ('AMIGOSIIIA', 'AMIGOSIIIB', 'AMIGOSIIIC'))(
    _UNIT(
        NAME='AMIGOSIIIA',
        MAC_ADDRESS='',
        SEABIRD_IDS=['90', '??'],
        AQUADOPP_IDS=['20', '21'],
        DATA_DIR='amigos3a',
    ),
    _UNIT(
        NAME='AMIGOSIIIB',
        MAC_ADDRESS='',
        SEABIRD_IDS=['05', '09'],
        AQUADOPP_IDS=['22', '23'],
        DATA_DIR='amigos3b',
    ),
    _UNIT(
        NAME='AMIGOSIIIC',
        MAC_ADDRESS='',
        SEABIRD_IDS=['06', '80'],
        AQUADOPP_IDS=['26', '27'],
        DATA_DIR='amigos3c',
    ),
)
# UNIT = *mac magic*


# --------------------------------------------------------------------------------
# SCHEDULE CONFIGURATION
# --------------------------------------------------------------------------------

_SCHEDULE_NAMES = (MODES.SUMMER, MODES.WINTER, MODES.TEST, MODES.SAFE)
SCHEDULE_NAMES = namedtuple('SCHEDULE_NAMES', _SCHEDULE_NAMES)(*_SCHEDULE_NAMES)

# Must be in order
# 1/1 - first date assumed to be last entry
SCHEDULE_START_TIMES = {
    SCHEDULE_NAMES.WINTER: {"month": 5, "day": 1},
    SCHEDULE_NAMES.SUMMER: {"month": 8, "day": 1},
}

# Time to wait in between schedule tasks/checks
SCHEDULE_SLEEP = 30

# --------------------------------------------------------------------------------
# GPIO
# --------------------------------------------------------------------------------

POWER_INDEX_DEVICE = "/sys/class/gpio/pwr_ctl/index"
POWER_DATA_DEVICE = "/sys/class/gpio/pwr_ctl/data"

SUPPLY_INDEX_DEVICE = "/sys/class/gpio/mcp3208-gpio/index"
SUPPLY_DATA_DEVICE = "/sys/class/gpio/mcp3208-gpio/data"

HUMIDITY_DATA_DEVICE = "/sys/class/hwmon/hwmon0/device/humidity1_input"
TEMPERATURE_DATA_DEVICE = "/sys/class/hwmon/hwmon0/device/temp1_input"

_GPIO = (
    'SBD',
    'GPS',
    'IMM',
    'WXT',
    'CRX',
    'WIN',
    'DTS',
    'CAM',
    'RTR',
    'HUB',
    'IRD',
    'V5E',
    'SER',
    'SOL',
)
GPIO = namedtuple('GPIO', _GPIO)(*_GPIO)

GPIO_CONFIG = {
    GPIO.SBD: {'index': 0, 'mask': int('0b00000001', 2), 'wait': 5},
    GPIO.GPS: {'index': 0, 'mask': int('0b00000010', 2), 'wait': 5},
    GPIO.IMM: {'index': 0, 'mask': int('0b00000100', 2), 'wait': 5},
    GPIO.WXT: {'index': 0, 'mask': int('0b00001000', 2), 'wait': 5},
    GPIO.CRX: {'index': 0, 'mask': int('0b00010000', 2), 'wait': 5},
    GPIO.WIN: {'index': 0, 'mask': int('0b01000000', 2), 'wait': 5},
    GPIO.DTS: {'index': 1, 'mask': int('0b00000001', 2), 'wait': 5},
    GPIO.CAM: {'index': 1, 'mask': int('0b00000010', 2), 'wait': 5},
    GPIO.RTR: {'index': 1, 'mask': int('0b00000100', 2), 'wait': 5},
    GPIO.HUB: {'index': 1, 'mask': int('0b00001000', 2), 'wait': 5},
    GPIO.IRD: {'index': 1, 'mask': int('0b00010000', 2), 'wait': 5},
    GPIO.V5E: {'index': 2, 'mask': int('0b00000001', 2), 'wait': 5},
    GPIO.SER: {'index': 2, 'mask': int('0b00000010', 2), 'wait': 5},
    GPIO.SOL: {'index': 2, 'mask': int('0b00001000', 2), 'wait': 5},
}

# --------------------------------------------------------------------------------
# Up/downlink
# --------------------------------------------------------------------------------

FTP_HOST = 'restricted_ftp'
FTP_TIMEOUT = 60
FTP_ORDERS_DIR = 'orders'
FTP_RESULTS_DIR = 'orders/results'
ORDERS_DIR = '/media/mmcblk0p1/orders'
RESULTS_DIR = '/media/mmcblk0p1/orders/results'
STAGED_UPLOAD_DIR = '/media/mmcblk0p1/staged'

# --------------------------------------------------------------------------------
# Up/downlink
# --------------------------------------------------------------------------------

SBD_MAX_SIZE = 1960
SBD_SIGNAL_WAIT = 10
SBD_SIGNAL_TRIES = 6
SBD_QUEUE_DIR = '/media/mmcblk0p1/sbd_queue'
SBD_QUEUE_MAX_TIME = 60 * 10

# --------------------------------------------------------------------------------
# Serial ports
# --------------------------------------------------------------------------------

SBD_PORT = '/dev/ttyS1'
SBD_BAUD = 9600
IMM_PORT = '/dev/ttyS4'
IMM_BAUD = 9600
