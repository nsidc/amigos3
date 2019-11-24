import os
import re
from datetime import datetime

import honcho.tasks.seabird as seabird
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
            elif re.match(r'#\d{2}DN\d+' + re.escape('\r\n'), res):
                os.write(
                    port,
                    (
                        b'#06DN6\r\n'
                        b'<RemoteReply>start sample number = 7770\r\n'
                        b'start time = 09 Oct 2019 14:50:01\r\n'
                        b'\r\n'
                        b'19.0395,  1.45496,   -1.627, 09 Oct 2019, 14:50:01, 7775\r\n'
                        b'19.1149,  1.45735,   -1.649, 09 Oct 2019, 15:00:01, 7775\r\n'
                        b'19.2158,  1.46027,   -1.644, 09 Oct 2019, 15:10:01, 7775\r\n'
                        b'19.2948,  1.46287,   -1.639, 09 Oct 2019, 15:20:01, 7775\r\n'
                        b'19.3569,  1.46486,   -1.635, 09 Oct 2019, 15:30:01, 7775\r\n'
                        b'19.4796,  1.46918,   -1.608, 09 Oct 2019, 15:40:01, 7775\r\n'
                        b'<Executed/>\r\n'
                        b'</RemoteReply>\r\n'
                        b'<Executed/>\r\n'
                        b'IMM>'
                    ),
                )

            else:
                os.write(port, b'ERROR\r\n')

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_query_smoke(imm_mock):
    seabird.query(imm_mock, device_id='06', samples=6)


def test_parse(imm_mock):
    expected_metadata = {
        'id': '06',
        'samples': 6,
        'start_time': datetime(2019, 10, 9, 14, 50, 1),
    }
    expected_data = [
        [datetime(2019, 10, 9, 14, 50, 1), 19.0395, 1.45496, -1.627],
        [datetime(2019, 10, 9, 15, 00, 1), 19.1149, 1.45735, -1.649],
        [datetime(2019, 10, 9, 15, 10, 1), 19.2158, 1.46027, -1.644],
        [datetime(2019, 10, 9, 15, 20, 1), 19.2948, 1.46287, -1.639],
        [datetime(2019, 10, 9, 15, 30, 1), 19.3569, 1.46486, -1.635],
        [datetime(2019, 10, 9, 15, 40, 1), 19.4796, 1.46918, -1.608],
    ]
    metadata, data = seabird.parse(seabird.query(imm_mock, device_id='06', samples=6))

    assert metadata == expected_metadata
    assert data == expected_data


def test_get_data(imm_mock, mocker):
    mocker.patch('honcho.tasks.seabird.Serial', lambda *args, **kwargs: imm_mock)
    mocker.patch('honcho.tasks.seabird.powered', mocker.stub())

    expected_data = [
        datetime(2019, 10, 9, 14, 50, 1),
        50.0,
        19.250249999999998,
        1.4615816666666666,
        -1.6336666666666668,
    ]
    data = seabird.get_data('06', samples=6)

    assert data == expected_data
