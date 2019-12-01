import re
from contextlib import contextmanager, closing
from logging import getLogger
from time import sleep

from serial import Serial

from honcho.config import (
    GPIO,
    IMM_PORT,
    IMM_BAUD,
    IMM_STARTUP_WAIT,
    IMM_COMMAND_TIMEOUT,
)
from honcho.util import serial_request
from honcho.core.gpio import powered

logger = getLogger(__name__)

RESPONSE_END = re.escape('<Executed/>\r\n')
REMOTE_RESPONSE_END = (
    re.escape('<Executed/>') + r'\s*' + re.escape('</RemoteReply>\r\n')
)


@contextmanager
def imm_components():
    with powered([GPIO.SER, GPIO.IMM]):
        sleep(IMM_STARTUP_WAIT)
        yield


@contextmanager
def power(serial):
    try:
        serial_request(serial, '\r\nPwrOn', RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)
        yield
    finally:
        serial_request(serial, '\r\nPwrOff', RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)


@contextmanager
def active_line():
    with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
        with power(serial):
            with force_capture_line(serial):
                yield serial


@contextmanager
def force_capture_line(serial):
    try:
        serial_request(
            serial, 'ForceCaptureLine', RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT
        )
        yield
    finally:
        serial_request(serial, 'ReleaseLine', RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)


def send_wakeup_tone(serial):
    serial_request(serial, 'SendWakeUpTone', RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)


def repl():
    with imm_components():
        with active_line() as serial:
            while True:
                print(serial.read(serial.inWaiting()))
                cmd = raw_input('> ')
                if cmd.lower() in ['quit', 'q']:
                    break
                serial.write(cmd + '\r\n')
                sleep(1)
                print(serial.read(serial.inWaiting()))
                sleep(3)
