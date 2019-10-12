import re
from contextlib import contextmanager
from logging import getLogger

from honcho.util import serial_request

logger = getLogger(__name__)


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
