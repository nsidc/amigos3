import os

import honcho.core.imm as imm
import pytest


@pytest.fixture
def imm_mock(serial_mock):
    def imm_listener(port):
        while 1:
            res = b""
            while not res.endswith(b"\r\n"):
                # keep reading one byte at a time until we have a full line
                res += os.read(port, 1)

            # write back the response
            if res == b'PwrOn\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'ForceCaptureLine\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'ReleaseLine\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'SendWakeUpTone\r\n':
                os.write(port, b'<Executing/>\r\n<Executed/>\r\n')
            else:
                os.write(port, b'ERROR\r\n')

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_power_smoke(imm_mock):
    imm.power(imm_mock)


def test_force_capture_line_smoke(imm_mock):
    with imm.force_capture_line(imm_mock):
        pass


def test_send_wakeup_tone_smoke(imm_mock):
    imm.send_wakeup_tone(imm_mock)
