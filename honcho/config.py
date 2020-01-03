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

LOG_DIR = '/media/mmcblk0p1/logs'
LOG_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def EXECUTION_LOG_FILEPATH(name):
    return os.path.join(ARCHIVE_DIR, '{0}.log'.format(name))


DEFAULT_LOG_LEVEL = 'INFO'
LOG_LEVEL = getattr(logging, os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL))

MAX_SYSTEM_SLEEP = 59
MIN_SYSTEM_VOLTAGE = 11
HUB_ALWAYS_ON = int(os.environ.get('HUB_ALWAYS_ON', 0))
KEEP_AWAKE = int(os.environ.get('KEEP_AWAKE', 0))
SKIP_MAINTENANCE = int(os.environ.get('SKIP_MAINTENANCE', 0))
IGNORE_LOW_VOLTAGE = int(os.environ.get('IGNORE_LOW_VOLTAGE', 0))


# --------------------------------------------------------------------------------
# UNIT SPECIFIC CONFIGURATION
# --------------------------------------------------------------------------------

_UNIT = namedtuple('UNIT', ('NAME', 'MAC_ADDRESS', 'SEABIRD_IDS', 'AQUADOPP_IDS'))

UNITS = namedtuple('UNITS', ('AMIGOSIIIA', 'AMIGOSIIIB', 'AMIGOSIIIC'))(
    _UNIT(
        NAME='AMIGOSIIIA',
        MAC_ADDRESS='70:b3:d5:65:46:05',
        SEABIRD_IDS=['05', '06', '07'],
        AQUADOPP_IDS=['20', '22', '24'],
    ),
    _UNIT(
        NAME='AMIGOSIIIB',
        MAC_ADDRESS='70:b3:d5:65:46:00',
        SEABIRD_IDS=['06', '08'],
        AQUADOPP_IDS=['23', '24'],
    ),
    _UNIT(
        NAME='AMIGOSIIIC',
        MAC_ADDRESS='70:b3:d5:65:46:03',
        SEABIRD_IDS=[],
        AQUADOPP_IDS=[],
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
SCHEDULE_IDLE_CHECK_INTERVAL = 30


SCHEDULES = {
    SCHEDULE_NAMES.WINTER: (
        ('scheduler.every().hour.at(":50")', 'seabird'),
        ('scheduler.every().hour.at(":52")', 'aquadopp'),
        ('scheduler.every().hour.at(":55")', 'crx'),
        ('scheduler.every().hour.at(":50")', 'weather'),
        ('scheduler.every().hour.at(":52")', 'solar'),
        ('scheduler.every().hour.at(":54")', 'sbd'),
        ('scheduler.every().day.at("00:10")', 'upload'),
        ('scheduler.every().day.at("06:10")', 'upload'),
        ('scheduler.every().day.at("18:10")', 'upload'),
        ('scheduler.every().day.at("20:10")', 'camera'),
        ('scheduler.every().day.at("21:05")', 'dts'),
        ('scheduler.every().day.at("23:10")', 'tps'),
        ('scheduler.every().day.at("12:10")', 'upload'),
    ),
    SCHEDULE_NAMES.SUMMER: (
        ('scheduler.every().hour.at(":45")', 'seabird'),  # 2 mins?
        ('scheduler.every().hour.at(":47")', 'solar'),  # 2 min
        ('scheduler.every().hour.at(":49")', 'aquadopp'),  # 2 mins?
        ('scheduler.every().hour.at(":50")', 'crx'),  # 1 min
        ('scheduler.every().hour.at(":52")', 'weather'),  # 2 min
        ('scheduler.every().hour.at(":55")', 'sbd'),
        #
        #
        #
        ('scheduler.every().day.at("03:00")', 'dts'),  # 6 mins
        ('scheduler.every().day.at("03:06")', 'upload'),
        ('scheduler.every().day.at("04:10")', 'camera'),  # 2 mins
        ('scheduler.every().day.at("04:15")', 'upload'),
        ('scheduler.every().day.at("05:10")', 'tps'),  # 20 mins
        #
        ('scheduler.every().day.at("07:00")', 'dts'),  # 6 mins
        ('scheduler.every().day.at("07:10")', 'upload'),
        #
        #
        #
        ('scheduler.every().day.at("11:05")', 'dts'),  # 6 mins
        ('scheduler.every().day.at("11:10")', 'tps'),  # 20 mins
        ('scheduler.every().day.at("12:00")', 'orders'),  # 20 mins
        ('scheduler.every().day.at("12:10")', 'camera'),  # 2 mins
        ('scheduler.every().day.at("12:15")', 'upload'),
        #
        #
        ('scheduler.every().day.at("15:00")', 'dts'),  # 6 mins
        #
        ('scheduler.every().day.at("17:10")', 'tps'),  # 20 mins
        #
        ('scheduler.every().day.at("19:00")', 'dts'),  # 6 mins
        ('scheduler.every().day.at("20:00")', 'upload'),
        ('scheduler.every().day.at("20:10")', 'camera'),  # 2 mins
        ('scheduler.every().day.at("20:15")', 'upload'),
        #
        #
        ('scheduler.every().day.at("23:00")', 'dts'),  # 6 mins
        ('scheduler.every().day.at("23:10")', 'tps'),  # 20 mins
    ),
    SCHEDULE_NAMES.TEST: (
        ('scheduler.every(1).minutes', 'seabird'),
        ('scheduler.every(1).minutes', 'solar'),
        ('scheduler.every(1).minutes', 'aquadopp'),
        ('scheduler.every(1).minutes', 'crx'),
        ('scheduler.every(1).minutes', 'gps'),
        ('scheduler.every(1).minutes', 'weather'),
        ('scheduler.every(1).minutes', 'dts'),
        ('scheduler.every(1).minutes', 'camera'),
        ('scheduler.every(1).minutes', 'tps'),
        ('scheduler.every(1).minutes', 'sbd'),
        ('scheduler.every(1).minutes', 'upload'),
        ('scheduler.every(1).minutes', 'orders'),
        ('scheduler.every(1).minutes', 'archive'),
    ),
    SCHEDULE_NAMES.SAFE: (('scheduler.every().day.at("12:00")', 'orders'),),
}

START_SCHEDULE_COMMAND = '/media/mmcblk0p1/honcho/bin/run_schedule.sh'
MAINTENANCE_HOUR = 0

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

SBD_PORT = '/dev/ttyS1'
SBD_BAUD = 9600
SBD_STARTUP_WAIT = 30
SBD_MAX_SIZE = 1960
SBD_SIGNAL_WAIT = 10
SBD_SIGNAL_TRIES = 6
SBD_WRITE_TIMEOUT = 30
SBD_TRANSMISSION_TIMEOUT = 60 * 5
IRD_DEFAULT_TIMEOUT = 10
SBD_QUEUE_MAX_TIME = 60 * 10
SBD_QUEUE_ROOT_DIR = '/media/mmcblk0p1/sbd_queue'


def SBD_QUEUE_DIR(tag):
    queue_dir = os.path.join(SBD_QUEUE_ROOT_DIR, tag)

    return queue_dir


# --------------------------------------------------------------------------------
# Up/downlink
# --------------------------------------------------------------------------------

FTP_HOST = 'restricted_ftp'
NETRC_FILEPATH = '/root/.netrc'
FTP_TIMEOUT = 3 * 60
DIALOUT_WAIT = 30
FTP_CONNECT_RETRIES = 18
FTP_RETRY_WAIT = 10
FTP_ORDERS_DIR = '/orders'
FTP_CHUNK_SIZE = 10000
JOINER_TEMPLATE = '/media/mmcblk0p1/honcho/core/joiner.pytemplate'


# --------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------

SEP = ','
DATA_ROOT_DIR = "/media/mmcblk0p1/data"

_DATA_TAGS = (
    'AQD',
    'SBD',
    'DTS',
    'GGA',
    'CAM',
    'WXT',
    'SOL',
    'CRX',
    'BNX',
    'TPS',
    'PWR',
    'MON',
    'ORD',
)
DATA_TAGS = namedtuple('DATA_TAGS', _DATA_TAGS)(*_DATA_TAGS)


def DATA_DIR(tag):
    data_dir = os.path.join(DATA_ROOT_DIR, tag)

    return data_dir


def DATA_LOG_FILENAME(tag):
    data_log_filepath = os.path.join(DATA_DIR(tag), tag + '.log')

    return data_log_filepath


TIMESTAMP_FMT = '%Y-%m-%dT%H:%M:%S'
TIMESTAMP_FILENAME_FMT = '%Y_%m_%d_%H_%M_%S'


# --------------------------------------------------------------------------------
# Upload
# --------------------------------------------------------------------------------

UPLOAD_QUEUE_DIR = '/media/mmcblk0p1/upload'
UPLOAD_CLEANUP = True
ARCHIVE_DIR = '/media/mmcblk0p1/archive'


# --------------------------------------------------------------------------------
# IMM
# --------------------------------------------------------------------------------

IMM_STARTUP_WAIT = 5
IMM_SHUTDOWN_WAIT = 20
IMM_COMMAND_TIMEOUT = 30
IMM_PORT = '/dev/ttyS4'
IMM_BAUD = 9600


# --------------------------------------------------------------------------------
# Camera
# --------------------------------------------------------------------------------

_SOAP_ACTION_KEYS = ('GET_STATUS', 'ABSOLUTE_MOVE')
SOAP_ACTION_KEYS = namedtuple('SOAP_ACTION_KEYS', _SOAP_ACTION_KEYS)(*_SOAP_ACTION_KEYS)

PTZ_SERVICE_URL = 'http://192.168.0.108/onvif/ptz_service'
SNAPSHOP_URL = (
    "http://192.168.0.108/onvifsnapshot/media_service/snapshot?channel=1&subtype=0"
)

SOAP_ACTIONS = {
    SOAP_ACTION_KEYS.GET_STATUS: 'http://www.onvif.org/ver20/ptz/wsdl/GetStatus',
    SOAP_ACTION_KEYS.ABSOLUTE_MOVE: 'http://www.onvif.org/ver20/ptz/wsdl/AbsoluteMove',
}
ONVIF_TEMPLATE_DIR = '/media/mmcblk0p1/honcho/tasks/onvif_templates'
ONVIF_TEMPLATE_FILES = {
    SOAP_ACTION_KEYS.GET_STATUS: 'get_status.xml',
    SOAP_ACTION_KEYS.ABSOLUTE_MOVE: 'absolute_move.xml',
}

CAMERA_USERNAME = 'admin'
CAMERA_PASSWORD = '10iLtxyh'
IMAGE_REDUCTION_FACTOR = '3/8'
CAMERA_STARTUP_WAIT = 60

_LOOKS = ('SOUTH', 'EAST', 'WEST', 'MIRROR', 'DOWN')
LOOKS = namedtuple('LOOKS', _LOOKS)(*_LOOKS)
PTZ = namedtuple('PTZ', ('pan', 'tilt', 'zoom'))
LOOK_PTZ = {
    LOOKS.DOWN: PTZ(pan=-0.09, tilt=-1, zoom=0),
    LOOKS.SOUTH: PTZ(pan=0.91, tilt=0.65, zoom=0),
    LOOKS.EAST: PTZ(pan=0.41, tilt=0.65, zoom=0),
    LOOKS.WEST: PTZ(pan=-0.61, tilt=0.65, zoom=0),
    LOOKS.MIRROR: PTZ(pan=-0.09, tilt=-1, zoom=1),
}
LOOK_SERIES = (LOOKS.MIRROR, LOOKS.SOUTH, LOOKS.EAST, LOOKS.WEST, LOOKS.DOWN)

CJPEG_COMMAND = '/media/mmcblk0p1/honcho/bin/cjpeg'
DJPEG_COMMAND = '/media/mmcblk0p1/honcho/bin/djpeg'


# --------------------------------------------------------------------------------
# CRX
# --------------------------------------------------------------------------------

CRX_URL = 'tcp:192.168.0.30:6785'
CRX_STARTUP_WAIT = 30


# --------------------------------------------------------------------------------
# Weather
# --------------------------------------------------------------------------------

WXT_PORT = '/dev/ttyS5'
WXT_BAUD = 115200
WXT_SAMPLES = 120


# --------------------------------------------------------------------------------
# GPS
# --------------------------------------------------------------------------------

GPS_PORT = '/dev/ttyS0'
GPS_BAUD = 115200
GPS_STARTUP_WAIT = 30
SECONDS_PER_MEASUREMENT = 30
MEASUREMENTS = 40


# --------------------------------------------------------------------------------
# Monitoring
# --------------------------------------------------------------------------------

WATCHDOG_DEVICE = '/sys/class/gpio/wdt_ctl/data'
DIRECTORIES_TO_MONITOR = {
    'data': DATA_ROOT_DIR,
    'archive': ARCHIVE_DIR,
    'sbd': SBD_QUEUE_ROOT_DIR,
    'upload': UPLOAD_QUEUE_DIR,
    'log': LOG_DIR,
}


# --------------------------------------------------------------------------------
# DTS
# --------------------------------------------------------------------------------

DTS_HOST = "192.168.0.50"  # win
DTS_USER = "admin"
DTS_PULL_DELAY = 60 * 6.5
DTS_WIN_DIR = 'Desktop/dts_data/xt19001/temperature/TARSAN'
DTS_CLEANUP_LOCAL = False
DTS_CLEANUP_REMOTE = False
DTS_FULL_RES_RANGES = [(250, 350), (3229 - 350, 3229 - 250)]


# --------------------------------------------------------------------------------
# Onboard sensors
# --------------------------------------------------------------------------------


def VOLTAGE_CONVERTER(value):
    '''
    Calibrated to < .01 V
    '''
    return 0.0063926 * value + 0.21706913


SOLAR_SAMPLES = 6
SOLAR_SAMPLE_WAIT = 5


# --------------------------------------------------------------------------------
# Ocean sensors
# --------------------------------------------------------------------------------


AQUADOPP_RECENT_SAMPLES = 1
SEABIRD_RECENT_SAMPLES = 6
