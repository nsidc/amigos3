import os
import re
from datetime import datetime

import pytest

import seabird


@pytest.fixture(autouse=True)
def short_serial_timeout(mocker):
    mocker.patch("imm.IMM_COMMAND_TIMEOUT", 3)


DD_RESPONSE = (
    b"<RemoteReply>start sample number = 1\r\n"
    b"start time = 09 Oct 2019 14:50:01\r\n"
    b"\r\n"
    b"3.00008,   1.0374,  713.998,  34.6688, 01:47:11, 31-12-2019, 3261\r\n"
    b"3.00027,   1.0386,  715.494,  34.6690, 01:47:21, 31-12-2019, 3261\r\n"
    b"3.00029,   1.0385,  715.544,  34.6694, 01:47:31, 31-12-2019, 3261\r\n"
    b"3.00028,   1.0383,  715.544,  34.6695, 01:47:41, 31-12-2019, 3261\r\n"
    b"3.00032,   1.0383,  716.070,  34.6697, 01:47:51, 31-12-2019, 3261\r\n"
    b"3.00031,   1.0382,  716.070,  34.6697, 01:48:01, 31-12-2019, 3261\r\n"
    b"<Executed/>\r\n"
    b"</RemoteReply>\r\n"
    b"<Executed/>\r\n"
)

SD_RESPONSE = (
    b"<RemoteReply>"
    b"<StatusData DeviceType='SBE37IMP' SerialNumber='03720050'>"
    b"<DateTime>2018-06-12T14:20:24</DateTime>"
    b"<EventSummary numEvents='18'/>"
    b"<Power>"
    b"<vMain>13.85</vMain>"
    b"<vLith> 3.21</vLith>"
    b"</Power>"
    b"<MemorySummary>"
    b"<Bytes>0</Bytes>"
    b"<Samples>6</Samples>"
    b"<SamplesFree>838860</SamplesFree>"
    b"<SampleLength>10</SampleLength>"
    b"</MemorySummary>"
    b"<AutonomousSampling>no, never started</AutonomousSampling>"
    b"</StatusData>"
    b"<Executed/>\r\n"
)


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
            elif re.match(r"#\d{2}DD\d+,\d+" + re.escape("\r\n"), res):
                os.write(port, DD_RESPONSE)
            elif re.match(r"#\d{2}GetSD" + re.escape("\r\n"), res):
                os.write(port, SD_RESPONSE)

            else:
                os.write(port, b"ERROR\r\n")

    with serial_mock(listener=imm_listener, baud=9600) as serial:
        yield serial


def test_query_samples_smoke(imm_mock):
    seabird.get_sample_range(imm_mock, device_id="06")


def test_get_sample_range(imm_mock, mocker):
    mocker.patch("imm.Serial", lambda *args, **kwargs: imm_mock)

    device_id = "06"
    expected = [
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 47, 11),
            conductivity="3.00008",
            temperature="1.0374",
            pressure="713.998",
            salinity="34.6688",
        ),
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 47, 21),
            conductivity="3.00027",
            temperature="1.0386",
            pressure="715.494",
            salinity="34.6690",
        ),
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 47, 31),
            conductivity="3.00029",
            temperature="1.0385",
            pressure="715.544",
            salinity="34.6694",
        ),
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 47, 41),
            conductivity="3.00028",
            temperature="1.0383",
            pressure="715.544",
            salinity="34.6695",
        ),
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 47, 51),
            conductivity="3.00032",
            temperature="1.0383",
            pressure="716.070",
            salinity="34.6697",
        ),
        seabird.SeabirdSample(
            timestamp=datetime(2019, 12, 31, 1, 48, 1),
            conductivity="3.00031",
            temperature="1.0382",
            pressure="716.070",
            salinity="34.6697",
        ),
    ]
    result = seabird.get_sample_range(imm_mock, device_id, 1, 6)

    assert result == expected
