import os
import string
from math import ceil
from datetime import datetime

import pytest

from honcho.config import SBD_MAX_SIZE, SBD_QUEUE_FILENAME
from honcho.core.iridium import message_size
from honcho.tasks.sbd import send, queue_sbd, send_queue, clear_queue


@pytest.fixture(autouse=True)
def skip_sleep(mocker):
    mocker.patch('honcho.tasks.sbd.sleep', mocker.stub())


@pytest.fixture
def sbd_mock(serial_mock, mocker):
    def read_line(port):
        res = b""
        while not res.endswith(b"\r\n"):
            # keep reading one byte at a time until we have a full line
            res += os.read(port, 1)
        return res

    def sbd_listener(port):
        while 1:
            res = read_line(port)
            # write back the response
            if res.upper() == b'AT+SBDD0\r\n':
                os.write(port, b'\r\n0\r\n\r\nOK\r\n')
            if res.upper() == b'AT\r\n':
                os.write(port, b'\r\nOK\r\n')
            elif res.upper() == b'AT+CSQ\r\n':
                os.write(port, b'\r\n+CSQ:5\r\n\r\nOK\r\n')
            elif res.upper() == b'AT+SBDWT\r\n':
                os.write(port, b'\r\nREADY\r\n')
                read_line(port)
                os.write(port, b'\r\n0\r\n\r\nOK\r\n')
            elif res.upper() == b'AT+SBDIX\r\n':
                os.write(port, b'\r\n+SBDIX: 0, 73, 0, 0, 0, 0\r\n\r\nOK\r\n')
            else:
                os.write(port, b'ERROR\r\n')

    with serial_mock(listener=sbd_listener, baud=9600) as serial:
        yield serial


def test_send_message(sbd_mock, mocker):
    mocker.patch('honcho.tasks.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.tasks.sbd.powered', mocker.stub())

    digits_size = message_size(string.digits)

    # Within size limit send ok
    multiples = int(ceil(SBD_MAX_SIZE // digits_size))
    message = (string.digits * multiples)[:SBD_MAX_SIZE]
    assert message_size(message) <= SBD_MAX_SIZE
    send(message)

    # Too big, raise exception
    multiples = int(ceil(SBD_MAX_SIZE // digits_size) + 1)
    message = string.digits * multiples
    assert message_size(message) > SBD_MAX_SIZE
    with pytest.raises(Exception):
        send(message)


def test_queue_sbd(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.tasks.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.tasks.sbd.powered', mocker.stub())
    mocker.patch('honcho.tasks.sbd.SBD_QUEUE_DIR', str(tmpdir))

    tag, message = 'tag', 'message'

    queue_sbd(message, tag)

    files = tmpdir.listdir()
    assert len(files) == 1

    sbd_file = files[0]
    assert sbd_file.read() == '{0},{1}'.format(tag, message)


def test_send_queue(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.tasks.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.tasks.sbd.SBD_QUEUE_DIR', str(tmpdir))
    send = mocker.MagicMock()
    mocker.patch('honcho.tasks.sbd.send', send)

    tag, message = 'tag', 'message'
    filename = SBD_QUEUE_FILENAME(tag=tag, timestamp=datetime.now())
    filepath = tmpdir.join(filename)
    filepath.write(message)

    send_queue(sbd_mock)

    assert send.called_once_with(message)
    assert not filepath.exists()


def test_clear_queue(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.tasks.sbd.SBD_QUEUE_DIR', str(tmpdir))

    tag, message = 'tag', 'message'
    filename = SBD_QUEUE_FILENAME(tag=tag, timestamp=datetime.now())
    filepath = tmpdir.join(filename)
    filepath.write(message)

    clear_queue()

    assert not filepath.exists()
