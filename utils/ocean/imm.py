import logging
import re
from contextlib import closing, contextmanager
from time import sleep

from serial import Serial

from util import serial_request

DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_BAUD = 9600
IMM_STARTUP_WAIT = 5
IMM_SHUTDOWN_WAIT = 20
IMM_COMMAND_TIMEOUT = 30
RESPONSE_END = re.escape("<Executed/>")
REMOTE_RESPONSE_END = (
    re.escape("<Executed/>") + r"\s*" + re.escape("</RemoteReply>\r\n")
)


@contextmanager
def power(serial):
    try:
        serial_request(serial, "\r\nPwrOn", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)
        yield
    finally:
        serial_request(serial, "\r\nPwrOff", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)
        sleep(IMM_SHUTDOWN_WAIT)


@contextmanager
def force_capture_line(serial):
    try:
        serial_request(
            serial, "ForceCaptureLine", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT
        )
        yield
    finally:
        serial_request(serial, "ReleaseLine", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)


@contextmanager
def active_line(port=DEFAULT_PORT, baud=DEFAULT_BAUD):
    with closing(Serial(port, baud)) as serial:
        with power(serial):
            with force_capture_line(serial):
                sleep(IMM_STARTUP_WAIT)
                yield serial


def console(port=DEFAULT_PORT, baud=DEFAULT_BAUD):
    with active_line(port, baud) as serial:
        print("Interactive console to IMM modem")
        print('Enter "quit" or "q" to quit')
        while True:
            print(serial.read(serial.inWaiting()))
            cmd = raw_input("> ")  # noqa
            if cmd.lower() in ["quit", "q"]:
                break
            serial.write(cmd + "\r\n")
            sleep(1)
            print(serial.read(serial.inWaiting()))
            sleep(3)


def get_status_xml(serial):
    raw = serial_request(serial, "GetSD", RESPONSE_END, timeout=10)
    status_xml = re.search(
        re.escape("<StatusData .*?>") + r".*" + re.escape("</StatusData>"),
        raw,
        flags=re.DOTALL,
    ).group(0)

    return status_xml


def get_discovery(serial):
    raw = serial_request(serial, "Disc", RESPONSE_END, timeout=10)
    status_xml = re.search(
        re.escape("<Discovery>") + r".*" + re.escape("</Discovery>"),
        raw,
        flags=re.DOTALL,
    ).group(0)

    return status_xml
