import os
import string
from math import ceil
from datetime import datetime

import pytest

from honcho.config import SBD_MAX_SIZE
from honcho.core.iridium import message_size
from honcho.tasks.sbd import (
    send,
    queue_sbd,
    send_queue,
    clear_queue,
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
    mocker.patch('honcho.tasks.sbd.Serial', lambda *args, **kwargs: sbd_mock)
    mocker.patch('honcho.tasks.sbd.SBD_QUEUE_DIR', str(tmpdir))
    send = mocker.MagicMock()
    mocker.patch('honcho.tasks.sbd.send', send)

    tag, message = 'test', 'message'
    filename = datetime.now().isoformat()
    directory = tmpdir.join(tag)
    directory.mkdir()
    filepath = tmpdir.join(tag).join(filename)
    filepath.write(message)

    send_queue(sbd_mock)

    assert send.called_once_with(message)
    assert not filepath.exists()


def test_clear_queue(tmpdir, sbd_mock, mocker):
    mocker.patch('honcho.tasks.sbd.SBD_QUEUE_DIR', str(tmpdir))

    tag, message = 'test', 'message'
    filename = datetime.now().isoformat()
    directory = tmpdir.join(tag)
    directory.mkdir()
    filepath = tmpdir.join(tag).join(filename)
    filepath.write(message)

    clear_queue()

    assert not filepath.exists()
