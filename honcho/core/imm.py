import re
from contextlib import contextmanager
from logging import getLogger
from time import sleep

from honcho.config import GPIO, DATA_LOG_FILENAME
from honcho.util import serial_request, serialize_datetime, deserialize_datetime
from honcho.core.gpio import powered

logger = getLogger(__name__)


@contextmanager
def imm_components():
    with powered([GPIO.IMM, GPIO.SER]):
        sleep(5)
        yield


def power_on(serial):
    expected = re.escape('<PowerOn/>\r\nIMM>')
    serial_request(serial, 'PwrOn', expected, timeout=10)


@contextmanager
def force_capture_line(serial):
    try:
        expected = (
            re.escape('ForceCaptureLine\r\n')
            + '('
            + re.escape('<Executing/>\r\n')
            + ')*'
            + re.escape('<Executed/>\r\nIMM>')
        )
        serial_request(serial, 'ForceCaptureLine', expected, timeout=5)
        yield
    finally:
        expected = (
            re.escape('ReleaseLine\r\n')
            + '('
            + re.escape('<Executing/>\r\n')
            + ')*'
            + re.escape('<Executed/>\r\nIMM>')
        )
        serial_request(serial, 'ReleaseLine', expected, timeout=5)


def send_wakeup_tone(serial):
    expected = (
        re.escape('SendWakeUpTone\r\n')
        + '('
        + re.escape('<Executing/>\r\n')
        + ')*'
        + re.escape('<Executed/>\r\nIMM>')
    )
    serial_request(serial, 'SendWakeUpTone', expected, timeout=10)


def log_data(s, tag):
    if not s.endswith('\n'):
        s += '\n'

    with open(DATA_LOG_FILENAME(tag), 'a') as f:
        f.write(s)


def serialize(data, device_id):
    serialized = ','.join([serialize_datetime(data[0]), device_id] + data)

    return serialized


def deserialize(serialized):
    split = serialized.split(',')

    deserialized = [deserialize_datetime(split[0]), split[1]] + [
        float(el) for el in split[2:]
    ]

    return deserialized
