import os

import pytest

from honcho.core.iridium import ping


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
    mocker.patch('honcho.tasks.sbd.powered', mocker.stub())

    ping(sbd_mock)
