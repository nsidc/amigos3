from collections import namedtuple
import logging
import os
import uuid
import re

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

# SEABIRD_IDS=['90', '80', '06', '05', '07', '08', '09'],

UNITS = namedtuple('UNITS', ('AMIGOSIIIA', 'AMIGOSIIIB', 'AMIGOSIIIC'))(
    _UNIT(
        NAME='AMIGOSIIIA',
        MAC_ADDRESS='70:b3:d5:65:46:05',
        SEABIRD_IDS=['05', '07', '08', '09'],
        AQUADOPP_IDS=['20', '21', '22'],
        DATA_DIR='amigos3a',
    ),
    _UNIT(
        NAME='AMIGOSIIIB',
        MAC_ADDRESS='70:b3:d5:65:46:00',
        SEABIRD_IDS=['05', '09'],
        AQUADOPP_IDS=['22', '23'],
        DATA_DIR='amigos3b',
    ),
    _UNIT(
        NAME='AMIGOSIIIC',
        MAC_ADDRESS='70:b3:d5:65:46:03',
        SEABIRD_IDS=['06', '80'],
        AQUADOPP_IDS=['26', '27'],
        DATA_DIR='amigos3c',
    ),
)

MAC_ADDRESS = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
try:
    UNIT = [unit for unit in UNITS if unit.MAC_ADDRESS == MAC_ADDRESS].pop()
except Exception:
    UNIT = UNITS.AMIGOSIIIA


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


SCHEDULES = {
    SCHEDULE_NAMES.WINTER: (
        ('hour', ":49", 'monitor'),
        ('day', "23:10", 'binex'),
        ('day', "20:10", 'camera'),
        ('hour', ":57", 'vaisala'),
        ('hour', ":50", 'seabird'),
        ('hour', ":52", 'aquadopp'),
        ('hour', ":55", 'cr1000x'),
        ('hour', ":56", 'solar'),
        ('day', "21:05", 'dts'),
        ('day', "06:10", 'archive'),
        ('day', "12:10", 'archive'),
        ('day', "18:10", 'archive'),
        ('day', "00:10", 'archive'),
        ('day', "00:00", 'orders'),
    ),
    SCHEDULE_NAMES.SUMMER: (
        ('hour', ":49", 'monitor'),
        ('day', "05:10", 'binex'),
        ('day', "11:10", 'binex'),
        ('day', "17:10", 'binex'),
        ('day', "23:10", 'binex'),
        ('day', "04:10", 'camera'),
        ('day', "12:10", 'camera'),
        ('day', "20:10", 'camera'),
        ('hour', ":57", 'vaisala'),
        ('hour', ":50", 'seabird'),
        ('hour', ":52", 'aquadopp'),
        ('hour', ":55", 'cr1000x'),
        ('hour', ":56", 'solar'),
        ('day', "03:05", 'dts'),
        ('day', "07:05", 'dts'),
        ('day', "11:05", 'dts'),
        ('day', "15:05", 'dts'),
        ('day', "19:05", 'dts'),
        ('day', "23:05", 'dts'),
        ('day', "06:10", 'archive'),
        ('day', "12:10", 'archive'),
        ('day', "18:10", 'archive'),
        ('day', "00:10", 'archive'),
        ('day', "00:00", 'orders'),
    ),
    SCHEDULE_NAMES.TEST: (
        # ('day', "00:00", 'monitor'),
        # ('day', "01:00", 'binex'),
        # ('day', "02:00", 'vaisala'),
        # ('day', "03:00", 'camera'),
        # ('day', "06:00", 'cr1000x'),
        # ('day', "07:00", 'solar'),
        ('hour', "04:00", 'seabird'),
        ('hour', "05:00", 'aquadopp'),
        # ('day', "08:00", 'dts'),
        # ('day', "09:00", 'archive'),
        # ('day', "10:00", 'orders'),
    ),
}


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
    GPIO.SBD: {'index': 0, 'mask': int('0b00000001', 2)},
    GPIO.GPS: {'index': 0, 'mask': int('0b00000010', 2)},
    GPIO.IMM: {'index': 0, 'mask': int('0b00000100', 2)},
    GPIO.WXT: {'index': 0, 'mask': int('0b00001000', 2)},
    GPIO.CRX: {'index': 0, 'mask': int('0b00010000', 2)},
    GPIO.WIN: {'index': 0, 'mask': int('0b01000000', 2)},
    GPIO.DTS: {'index': 1, 'mask': int('0b00000001', 2)},
    GPIO.CAM: {'index': 1, 'mask': int('0b00000010', 2)},
    GPIO.RTR: {'index': 1, 'mask': int('0b00000100', 2)},
    GPIO.HUB: {'index': 1, 'mask': int('0b00001000', 2)},
    GPIO.IRD: {'index': 1, 'mask': int('0b00010000', 2)},
    GPIO.V5E: {'index': 2, 'mask': int('0b00000001', 2)},
    GPIO.SER: {'index': 2, 'mask': int('0b00000010', 2)},
    GPIO.SOL: {'index': 2, 'mask': int('0b00001000', 2)},
}

# --------------------------------------------------------------------------------
# Up/downlink
# --------------------------------------------------------------------------------

FTP_HOST = 'restricted_ftp'
FTP_TIMEOUT = 60
FTP_CONNECT_RETRIES = 2
FTP_ORDERS_DIR = 'orders'
FTP_RESULTS_DIR = 'orders/results'
ORDERS_DIR = '/media/mmcblk0p1/orders'
RESULTS_DIR = '/media/mmcblk0p1/orders/results'

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

# --------------------------------------------------------------------------------
# DTS
# --------------------------------------------------------------------------------

DTS_HOST = "192.168.0.50"
DTS_USER = "admin"
DTS_PULL_DELAY = 60 * 5
DTS_WIN_DATA_DIR = 'Desktop/dts_data'
DTS_RAW_DATA_DIR = "/media/mmcblk0p1/data/dts_raw"
DTS_CLEANUP_LOCAL = True
DTS_CLEANUP_REMOTE = True
DTS_FULL_RES_RANGES = [(1000, 1200), (2000, 2200)]

# --------------------------------------------------------------------------------
# Onboard sensors
# --------------------------------------------------------------------------------


def VOLTAGE_CONVERTER(value):
    '''
    Calibrated to < .01 V
    '''
    return 0.0063926 * value + 0.21706913


# --------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------

SEP = ','
DATA_ROOT_DIR = "/media/mmcblk0p1/data"

_DATA_TAGS = ('AQD', 'SBD', 'DTS', 'GPS', 'CAM')
DATA_TAGS = namedtuple('DATA_TAGS', _DATA_TAGS)(*_DATA_TAGS)


def DATA_DIR(tag):
    data_dir = os.path.join(DATA_ROOT_DIR, tag)

    return data_dir


def DATA_LOG_FILENAME(tag):
    data_dir = os.path.join(DATA_DIR(tag), tag + '.log')

    return data_dir


# --------------------------------------------------------------------------------
# Upload
# --------------------------------------------------------------------------------

STAGED_UPLOAD_DIR = '/media/mmcblk0p1/staged'
UPLOAD_CLEANUP = True
UPLOAD_DATA_TAGS = (DATA_TAGS.DTS, DATA_TAGS.GPS, DATA_TAGS.CAM)
DATASTORE_DIR = '/media/mmcblk0p1/datastore'

# --------------------------------------------------------------------------------
# IMM
# --------------------------------------------------------------------------------

IMM_STARTUP_WAIT = 5
IMM_COMMAND_TIMEOUT = 30
