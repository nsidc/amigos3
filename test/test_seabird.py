import os
import re
from datetime import datetime

import honcho.tasks.seabird as seabird
import pytest


@pytest.fixture(autouse=True)
def short_serial_timeout(mocker):
    mocker.patch('honcho.core.imm.IMM_COMMAND_TIMEOUT', 3)


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
            elif res == b'PwrOff\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'ForceCaptureLine\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'ReleaseLine\r\n':
                os.write(port, b'<Executed/>\r\n')
            elif res == b'SendWakeUpTone\r\n':
                os.write(port, b'<Executing/>\r\n<Executed/>\r\n')
            elif re.match(r'#\d{2}DN\d+' + re.escape('\r\n'), res):
                os.write(
                    port,
                    (
                        b'<RemoteReply>start sample number = 7770\r\n'
                        b'start time = 09 Oct 2019 14:50:01\r\n'
                        b'\r\n'
                        b'19.0395,  1.45496,   -1.627, 34.184, 09 Oct 2019, 14:50:01, 7775\r\n'  # noqa
                        b'19.1149,  1.45735,   -1.649, 34.284, 09 Oct 2019, 15:00:01, 7775\r\n'  # noqa
                        b'19.2158,  1.46027,   -1.644, 34.384, 09 Oct 2019, 15:10:01, 7775\r\n'  # noqa
                        b'19.2948,  1.46287,   -1.639, 34.484, 09 Oct 2019, 15:20:01, 7775\r\n'  # noqa
                        b'19.3569,  1.46486,   -1.635, 34.584, 09 Oct 2019, 15:30:01, 7775\r\n'  # noqa
                        b'19.4796,  1.46918,   -1.608, 34.684, 09 Oct 2019, 15:40:01, 7775\r\n'  # noqa
                        b'<Executed/>\r\n'
                        b'</RemoteReply>\r\n'
                        b'<Executed/>\r\n'
                    ),
                )
            elif re.match(r'#\d{2}GetSD' + re.escape('\r\n'), res):
                os.write(
                    port,
                    (
                        b'<RemoteReply>'
                        b"<StatusData DeviceType='SBE37IMP' SerialNumber='03720050'>"
                        b"<DateTime>2018-06-12T14:20:24</DateTime>"
                        b"<EventSummary numEvents='18'/>"
                        b"<Power>"
                        b"<vMain>13.85</vMain>"
                        b"<vLith> 3.21</vLith>"
                        b"</Power>"
                        b"<MemorySummary>"
                        b"<Bytes>0</Bytes>"
                        b"<Samples>0</Samples>"
                        b"<SamplesFree>838860</SamplesFree>"
                        b"<SampleLength>10</SampleLength>"
                        b"</MemorySummary>"
                        b"<AutonomousSampling>no, never started</AutonomousSampling>"
                        b"</StatusData>"
                    ),
                )

            else:
                os.write(port, b'ERROR\r\n')

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_query_samples_smoke(imm_mock):
    seabird.query_samples(imm_mock, device_id='06', n=6)


def test_get_recent_samples(imm_mock, mocker):
    mocker.patch('honcho.core.imm.Serial', lambda *args, **kwargs: imm_mock)
    mocker.patch('honcho.core.imm.powered', mocker.stub())

    device_id = '06'
    expected = [
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 14, 50, 1), '06', 19.0395, 1.45496, -1.627, 34.184
        ),
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 00, 1), '06', 19.1149, 1.45735, -1.649, 34.284
        ),
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 10, 1), '06', 19.2158, 1.46027, -1.644, 34.384
        ),
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 20, 1), '06', 19.2948, 1.46287, -1.639, 34.484
        ),
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 30, 1), '06', 19.3569, 1.46486, -1.635, 34.584
        ),
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 40, 1), '06', 19.4796, 1.46918, -1.608, 34.684
        ),
    ]
    result = seabird.get_recent_samples([device_id], n=6)

    assert result == expected


def test_get_averaged_sample(imm_mock, mocker):
    mocker.patch('honcho.core.imm.Serial', lambda *args, **kwargs: imm_mock)
    mocker.patch('honcho.core.imm.powered', mocker.stub())

    expected = [
        seabird.SeabirdSample(
            datetime(2019, 10, 9, 15, 15, 1),
            '06',
            19.250249999999998,
            1.4615816666666666,
            -1.6336666666666668,
            34.434,
        )
    ]
    result = seabird.get_averaged_samples(['06'], n=6)

    assert result == expected
