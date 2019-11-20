import re
import os
from contextlib import closing
from datetime import datetime

from serial import Serial

from honcho.config import (
    SBD_MAX_SIZE,
    SBD_PORT,
    SBD_BAUD,
    SBD_SIGNAL_TRIES,
    SBD_QUEUE_DIR,
    SBD_QUEUE_MAX_TIME,
)
from honcho.core.gpio import powered
from honcho.util import serial_request, fail_gracefully


def _ping_iridium(serial):
    expected = re.escape('OK\r\n')
    try:
        serial_request(serial, 'AT', expected, timeout=10)
    except Exception:
        raise Exception("Iridium did not respond correctly to ping")


def _check_signal(serial):
    expected = re.escape('+CSQ: ') + r'(?P<strength>\d)' + re.escape('\r\n')
    try:
        response = serial_request(serial, 'AT+CSQ', expected, timeout=10)
    except Exception:
        raise Exception("Iridium did not respond correctly to signal query")

    strength = re.search(expected, response).groupdict()['strength']

    return strength


def message_size(message):
    size = len(message.encode('utf-8'))
    return size


def _send_message(serial, message):
    size = message_size(message)
    assert size <= SBD_MAX_SIZE, "Message is too large: {0} > {1}".format(
        size, SBD_MAX_SIZE
    )

    for _ in xrange(SBD_SIGNAL_TRIES):
        signal = _check_signal(serial)
        if signal < 4:
            continue

    # Initiate write text
    expected = 'READY\r\n'
    serial_request(serial, 'AT+SBDWT', expected, timeout=10)

    # Submit message
    expected = r'(?P<status>\d)' + re.escape('\r\n')
    response = serial_request(serial, message, expected, timeout=10)
    status = int(re.search(expected, response).groupdict()['status'])
    if status:
        raise Exception('SBD write command returned error status')

    # Initiate transfer to GSS
    expected = (
        re.escape('+SBDIX: ')
        + (
            r'(?P<mo_status>\d+), '
            r'(?P<momsn>\d+), '
            r'(?P<mt_status>\d+), '
            r'(?P<mtmsn>\d+), '
            r'(?P<mt_length>\d+), '
            r'(?P<mt_queued>\d+)'
        )
        + re.escape('\r\n')
    )
    serial_request(serial, 'AT+SBDIX', expected, timeout=10)


def _clear_mo_buffer(serial):
    expected = r'(?P<status>\d)' + re.escape('\r\n')
    response = serial_request(serial, 'AT+SBDD0', re.escape('\r\n'), timeout=10)
    status = int(re.search(expected, response).groupdict()['status'])
    if status:
        raise Exception('SBD clear mo command returned error status')


def _build_queue():
    queue = []
    for dirpath, _, filenames in os.walk(SBD_QUEUE_DIR):
        queue.extend([os.path.join(dirpath, filename) for filename in filenames])

    queue = sorted(queue, key=lambda x: os.path.split(x)[-1])

    return queue


def _send_queued(serial, timeout):
    queue = _build_queue()
    for filepath in queue:
        with open(filepath, 'r') as f:
            tag = os.path.split(filepath)[-2]
            _send_message(serial=serial, message=tag + ',' + f.read())
            os.remove(filepath)


def send_message(message):
    with powered('ird'), powered('sbd'), powered('ser'):
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            _send_message(serial, message)


def send_queue(timeout=SBD_QUEUE_MAX_TIME):
    with powered('ird'), powered('sbd'), powered('ser'):
        with closing(Serial(SBD_PORT, SBD_BAUD)) as serial:
            _send_queued(serial, timeout)


def queue_sbd(tag, message):
    filepath = os.path.join(SBD_QUEUE_DIR, tag, datetime.now().isoformat())
    with open(filepath, 'w') as f:
        f.write(tag + ',' + message)


def clear_queue():
    queue = _build_queue()
    for filepath in queue:
        os.remove(filepath)


@fail_gracefully
def execute():
    send_queue()


if __name__ == '__main__':
    execute()
