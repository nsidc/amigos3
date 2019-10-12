import os

import honcho.core.imm as imm
import pytest


@pytest.fixture
def imm_mock(serial_port_mock):
    def imm_listener(port):
        while 1:
            res = b""
            while not res.endswith(b"\r\n"):
                # keep reading one byte at a time until we have a full line
                res += os.read(port, 1)

            # write back the response
            if res == b'PwrOn\r\n':
                os.write(port, b'<PowerOn/>\r\nIMM>')
            elif res == b'ForceCaptureLine\r\n':
                os.write(port, b'FCL\r\n<Executed/>\r\nIMM>')
            elif res == b'ReleaseLine\r\n':
                os.write(port, b'ReleaseLine\r\n<Executed/>\r\nIMM>')
            elif res == b'SendWakeUpTone\r\n':
                os.write(port, b'SendWakeUpTone\r\n<Executing/>\r\n<Executed/>\r\nIMM>')

    yield serial_port_mock(listener=imm_listener, baud=9600)


def test_power_on(imm_mock):
    imm.power_on(imm_mock)


def test_force_capture_line(imm_serial_mock):
    with imm.force_capture_line(imm_serial_mock):
        pass


def test_send_wakeup_tone(imm_serial_mock):
    imm.send_wakeup_tone(imm_serial_mock)
