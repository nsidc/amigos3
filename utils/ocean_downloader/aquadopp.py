import datetime
import logging
import os
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from time import sleep

from imm import (DEFAULT_BAUD, DEFAULT_PORT, REMOTE_RESPONSE_END, RESPONSE_END,
                 active_line, wait_for_comms)
from util import chunk_filepath, serial_request, write_chunk

logger = logging.getLogger(__name__)

AQUADOPP_DATA_DIR = "seabird_data"
_DATA_KEYS = (
    "timestamp",
    "device_id",
    "unknown1",
    "unknown2",
    "error",
    "status",
    "east_vel",
    "north_vel",
    "up_vel",
    "east_ampl",
    "north_ampl",
    "up_ampl",
    "voltage",
    "sound_speeD",
    "heading",
    "pitch",
    "roll",
    "pressure",
    "temperaturE",
    "analogue1",
    "analogue2",
    "speed",
    "direction",
)
DATA_KEYS = namedtuple("DATA_KEYS", (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
AquadoppSample = namedtuple("AquadoppSample", DATA_KEYS)


def get_status_xml(serial, device_id):
    raw = serial_request(
        serial, "!{0}SampleGetSummary".format(device_id), RESPONSE_END, timeout=10
    )
    status_xml = re.search(
        re.escape("<SampleDataSummary") + r".*" + re.escape("/>"),
        raw,
        flags=re.DOTALL,
    ).group(0)

    return status_xml


def get_status(serial, device_id):
    status_xml = get_status_xml(serial, device_id)
    status_data = ET.fromstring(status_xml)
    status = {
        "samples": status_data.attrib["NumSamples"],
        "total_len": status_data.attrib["TotalLen"],
        "free_mem": status_data.attrib["FreeMem"],
    }

    return status


def wait_for_comms(serial):
    """
    Check for status response on serial IMM connection
    """
    while True:
        try:
            get_status(serial)
        except:  # noqa
            logger.debug(
                "No response to SampleGetSummary, fiddle with cable and i'll try again..."
            )
            sleep(10)
        else:
            break


def pull_samples(
    device_id,
    start=None,
    end=None,
    chunk_size=100,
    port=DEFAULT_PORT,
    baud=DEFAULT_BAUD,
):
    """
    Get samples for 'device_id' in range 'start' to 'end' in chunks and write to output directory.

    Chunks already stored will be skipped.
    """
    samples = []
    with active_line(port, baud) as serial:
        if start is None:
            start = 1
        if end is None:
            status = get_status(serial, device_id)
            end = status["samples"]

        chunk_start = start - (start % chunk_size)
        chunk_end = end - (end % chunk_size) + chunk_size

        wait_for_comms(serial)
        for i in range(chunk_start, chunk_end, chunk_size):
            filepath = chunk_filepath(
                device_id, chunk_start, chunk_end, AQUADOPP_DATA_DIR
            )

            raw = query_sample_list(serial, device_id)
            sample_list = parse_sample_list(raw)

            if not os.path.exists(filepath):
                samples = []
                for sample_id in sample_list[i : i + chunk_size]:
                    raw = query_sample(serial, device_id, sample_id)
                    samples.append(parse_sample(device_id, raw))

                write_chunk(samples, filepath)
            else:
                logger.debug(
                    "Chunk found, skipping: {0}, {1}:{2}".format(
                        device_id, chunk_start, chunk_end
                    )
                )


def query_sample_list(serial, device_id):
    expected_response = re.escape("</SampleList>\r\n") + REMOTE_RESPONSE_END
    raw = serial_request(
        serial, "!{0}SampleGetList".format(device_id), expected_response, timeout=5
    )

    return raw


def query_sample(serial, device_id, sample_id):
    expected_response = re.escape("</SampleData>\r\n") + REMOTE_RESPONSE_END
    raw = serial_request(
        serial,
        "!{0}SampleGetData:{1}".format(device_id, sample_id),
        expected_response,
        timeout=5,
    )

    return raw


def parse_sample(device_id, raw):
    pattern = (
        ".*"
        + re.escape("<SampleData ")
        + "(?P<metadata>.*)"
        + re.escape(">")
        + "(?P<data>.*)"
        + re.escape("\r\n")
        + re.escape("</SampleData>")
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    # header = dict([el.split('=') for el in match.group('metadata').strip().split()])
    values = match.group("data").strip().split()

    timestamp = datetime.strptime(" ".join(values[:4]), "%m %d %Y %H")
    sample = AquadoppSample(
        timestamp=timestamp,
        device_id=device_id,
        **dict((key, values[4 + i]) for i, key in enumerate(DATA_KEYS[2:]))
    )

    return sample


def parse_sample_list(raw):
    list_pattern = (
        re.escape("<SampleList>") + "(?P<list>.*)" + re.escape("</SampleList>")
    )
    id_pattern = r" ID='(?P<id>.*?)' "

    match = re.search(list_pattern, raw, flags=re.DOTALL)

    sample_list = match.group("list").strip().split("\r\n")
    ids = [re.search(id_pattern, sample).groupdict()["id"] for sample in sample_list]

    return ids
