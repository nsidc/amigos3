import re
from contextlib import contextmanager
from logging import getLogger

from honcho.core.serial import serial_request

logger = getLogger(__name__)


def power_on(serial):
    expected = re.escape('<PowerOn/>\r\nIMM>')
    serial_request(serial, 'PwrOn', expected, timeout=10)


@contextmanager
def force_capture_line(serial):
    try:
        expected = re.escape('ForceCaptureLine\r\n<Executed/>\r\nIMM>')
        serial_request(serial, 'ForceCaptureLine', expected, timeout=5)
        yield
    finally:
        expected = re.escape('ReleaseLine\r\n<Executed/>\r\nIMM>')
        serial_request(serial, 'ReleaseLine', expected, timeout=5)


def send_wakeup_tone(serial):
    expected = re.escape(
        'SendWakeUpTone\r\n' '(<Executing/>\r\n)*' '<Executed/>\r\n' 'IMM>'
    )
    serial_request(serial, 'SendWakeUpTone', expected, timeout=10)
