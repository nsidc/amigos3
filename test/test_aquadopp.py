import os
import re
from datetime import datetime

import honcho.core.aquadopp as aquadopp
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
                os.write(port, b'<PowerOn/>\r\nIMM>')
            elif res == b'ForceCaptureLine\r\n':
                os.write(port, b'ForceCaptureLine\r\n<Executed/>\r\nIMM>')
            elif res == b'ReleaseLine\r\n':
                os.write(port, b'ReleaseLine\r\n<Executed/>\r\nIMM>')
            elif res == b'SendWakeUpTone\r\n':
                os.write(port, b'SendWakeUpTone\r\n<Executing/>\r\n<Executed/>\r\nIMM>')
            elif re.match(r'!\d{2}SAMPLEGETLAST' + re.escape('\r\n'), res):
                os.write(
                    port,
                    (
                        b'!20SAMPLEGETLAST\r\n'
                        b'<RemoteReply><Executing/>\r\n'
                        b'<SampleData ID=\'0x00000774\' Len=\'111\' CRC=\'0xCDB08DA1\'>'
                        b'10 9 2019 15 0 0 0 48 -0.043 0.059 -0.105 159 135 155 13.1 '
                        b'1519.8 39.8 -11.6 0.5 0.000 19.43 0 0 0.073 323.9\r\n'
                        b'</SampleData>\r\n'
                        b'<Executed/></RemoteReply>\r\n'
                        b'<Executed/>\r\n'
                        b'IMM>'
                    ),
                )

            else:
                os.write(port, b'ERROR\r\n')

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_query_smoke(imm_mock):
    aquadopp.query(imm_mock, device_id='20')


def test_parse(imm_mock):
    expected_metadata = {'error': 0, 'status': 0, 'id': '20'}
    expected_data = [
        datetime(2019, 10, 9, 15, 0, 0),
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
    ]
    metadata, data = aquadopp.parse(aquadopp.query(imm_mock, device_id='20'))

    assert metadata == expected_metadata
    assert data == expected_data


def test_get_data(imm_mock, mocker):
    mocker.patch('honcho.core.aquadopp.Serial', lambda *args, **kwargs: imm_mock)
    mocker.patch('honcho.core.aquadopp.powered', mocker.stub())

    expected_data = [
        datetime(2019, 10, 9, 15, 0, 0),
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
    ]
    data = aquadopp.get_data('20')

    assert data == expected_data
