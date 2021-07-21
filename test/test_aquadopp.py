import os
import re
from datetime import datetime

import honcho.tasks.aquadopp as aquadopp
import pytest


@pytest.fixture(autouse=True)
def short_serial_timeout(mocker):
    mocker.patch("honcho.core.imm.IMM_COMMAND_TIMEOUT", 3)


@pytest.fixture
def imm_mock(serial_mock):
    def imm_listener(port):
        while 1:
            res = b""
            while not res.endswith(b"\r\n"):
                # keep reading one byte at a time until we have a full line
                res += os.read(port, 1)

            # write back the response
            if res == b"PwrOn\r\n":
                os.write(port, b"<Executed/>\r\n")
            elif res == b"PwrOff\r\n":
                os.write(port, b"<Executed/>\r\n")
            elif res == b"ForceCaptureLine\r\n":
                os.write(port, b"<Executed/>\r\n")
            elif res == b"ReleaseLine\r\n":
                os.write(port, b"<Executed/>\r\n")
            elif res == b"SendWakeUpTone\r\n":
                os.write(port, b"<Executing/>\r\n<Executed/>\r\n")
            elif re.match(r"!\d{2}SampleGetLast" + re.escape("\r\n"), res):
                os.write(
                    port,
                    (
                        b"<RemoteReply><Executing/>\r\n"
                        b"<SampleData ID='0x00000774' Len='111' CRC='0xCDB08DA1'>"
                        b"10 9 2019 15 0 0 0 48 -0.043 0.059 -0.105 159 135 155 13.1 "
                        b"1519.8 39.8 -11.6 0.5 0.000 19.43 0 0 0.073 323.9\r\n"
                        b"</SampleData>\r\n"
                        b"<Executed/></RemoteReply>\r\n"
                        b"<Executed/>\r\n"
                    ),
                )

            else:
                os.write(port, b"ERROR\r\n")

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_query_last_sample_smoke(imm_mock):
    aquadopp.query_last_sample(imm_mock, device_id="20")


def test_parse_sample(imm_mock):
    expected = aquadopp.AquadoppSample(
        datetime(2019, 10, 9, 15, 0, 0),
        "20",
        0,
        0,
        0,
        48,
        -0.043,
        0.059,
        -0.105,
        159,
        135,
        155,
        13.1,
        1519.8,
        39.8,
        -11.6,
        0.5,
        0.000,
        19.43,
        0,
        0,
        0.073,
        323.9,
    )
    result = aquadopp.parse_sample(
        "20", aquadopp.query_last_sample(imm_mock, device_id="20")
    )

    assert result == expected


def test_get_recent_samples(imm_mock, mocker):
    mocker.patch("honcho.core.imm.Serial", lambda *args, **kwargs: imm_mock)
    mocker.patch("honcho.core.imm.powered", mocker.stub())

    expected = [
        aquadopp.AquadoppSample(
            datetime(2019, 10, 9, 15, 0, 0),
            "20",
            0,
            0,
            0,
            48,
            -0.043,
            0.059,
            -0.105,
            159,
            135,
            155,
            13.1,
            1519.8,
            39.8,
            -11.6,
            0.5,
            0.000,
            19.43,
            0,
            0,
            0.073,
            323.9,
        )
    ]
    result = aquadopp.get_recent_samples(["20"], n=1)

    assert result == expected
