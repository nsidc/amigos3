import os
import string
from math import ceil
from datetime import datetime

import pytest

from honcho.config import SBD_MAX_SIZE
from honcho.core.sbd import (
    send_message,
    message_size,
    queue_sbd,
    send_queue,
    clear_queue,
    _ping_iridium,
)


@pytest.fixture
def sbd_mock(serial_mock, mocker):
    def sbd_listener(port):
        while 1:
            res = b""
            while not res.endswith(b"\r\n"):
                # keep reading one byte at a time until we have a full line
                res += os.read(port, 1)

            # write back the response
            if res == b'AT\r\n':
                os.write(port, b'OK\r\n')
            elif res == b'AT+CSQ\r\n':
                os.write(port, b'+CSQ:5\r\n')
            elif res == b'AT+SBDWT\r\n':
                os.write(port, b'READY\r\n')
            elif res == b'AT+SBDIX\r\n':
                os.write(port, b'+SBDIX: 0, 1, 0, 2, 0, 0\r\n')
            else:
                os.write(port, b'0\r\n')

    with serial_mock(listener=sbd_listener, baud=9600) as serial:
        yield serial


def test_smoke_ping_iridium(sbd_mock, mocker):
    mocker.patch('honcho.core.sbd.powered', mocker.stub())

    _ping_iridium(sbd_mock)


def test_send_message(sbd_mock, mocker):
    mocker.patch('honcho.core.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.core.sbd.powered', mocker.stub())

    digits_size = message_size(string.digits)

    # Within size limit send ok
    multiples = int(ceil(SBD_MAX_SIZE // digits_size))
    message = (string.digits * multiples)[:SBD_MAX_SIZE]
    assert message_size(message) <= SBD_MAX_SIZE
    send_message(message)

    # Too big, raise exception
    multiples = int(ceil(SBD_MAX_SIZE // digits_size) + 1)
    message = string.digits * multiples
    assert message_size(message) > SBD_MAX_SIZE
    with pytest.raises(Exception):
        send_message(message)


def test_queue_sbd(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.core.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.core.sbd.powered', mocker.stub())
    mocker.patch('honcho.core.sbd.SBD_QUEUE_DIR', str(tmpdir))

    tag, message = 'test', 'message'

    queue_sbd(tag, message)

    dirs = tmpdir.listdir()
    assert len(dirs) == 1
    assert dirs[0].basename == tag

    files = tmpdir.join(tag).listdir()
    assert len(files) == 1
    # assert re.matches(pattern, files[0].basename)

    sbd_file = files[0]
    assert sbd_file.read() == '{0},{1}'.format(tag, message)


def test_send_queue(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.core.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.core.sbd.SBD_QUEUE_DIR', str(tmpdir))
    mocker.patch('honcho.core.sbd.powered', mocker.stub())
    send_message = mocker.MagicMock()
    mocker.patch('honcho.core.sbd.send_message', send_message)

    tag, message = 'test', 'message'
    filename = datetime.now().isoformat()
    directory = tmpdir.join(tag)
    directory.mkdir()
    filepath = tmpdir.join(tag).join(filename)
    filepath.write(message)

    send_queue()

    assert send_message.called_once_with(message)
    assert not filepath.exists()


def test_clear_queue(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.core.sbd.SBD_QUEUE_DIR', str(tmpdir))

    tag, message = 'test', 'message'
    filename = datetime.now().isoformat()
    directory = tmpdir.join(tag)
    directory.mkdir()
    filepath = tmpdir.join(tag).join(filename)
    filepath.write(message)

    clear_queue()

    assert not filepath.exists()
