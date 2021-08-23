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

SEABIRD_DATA_DIR = "seabird_data"
_DATA_KEYS = (
    "timestamp",
    "conductivity",
    "temperature",
    "pressure",
    "salinity",
)
DATA_KEYS = namedtuple("DATA_KEYS", (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
SeabirdSample = namedtuple("SeabirdSample", DATA_KEYS)


def get_status_xml(serial, device_id):
    raw = serial_request(
        serial, "#{0}GetSD".format(device_id), RESPONSE_END, timeout=10
    )
    status_xml = re.search(
        re.escape("<StatusData>") + r".*" + re.escape("</StatusData>"),
        raw,
        flags=re.DOTALL,
    ).group(0)

    return status_xml


def get_status(serial, device_id):
    status_xml = get_status_xml(serial, device_id)
    status_data = ET.fromstring(status_xml)
    status = status_data.attrib
    status["datetime"] = datetime.strptime(
        status_data.find("DateTime").text, "%Y-%m-%dT%H:%M:%S"
    )
    status["voltage"] = float(status_data.find("Power/vMain").text)
    status["voltage_li"] = float(status_data.find("Power/vLith").text)
    status["bytes"] = int(status_data.find("MemorySummary/Bytes").text)
    status["samples"] = int(status_data.find("MemorySummary/Samples").text)
    status["samples_free"] = int(status_data.find("MemorySummary/SamplesFree").text)
    status["samples_length"] = int(status_data.find("MemorySummary/SampleLength").text)
    status["sampling"] = status_data.find("AutonomousSampling").text

    return status


def wait_for_comms(serial):
    """
    Check for status response on serial IMM connection
    """
    while True:
        try:
            get_status(serial)
        except:  # noqa
            logger.debug("No response to GetSD, fiddle with cable and ill try again...")
            sleep(10)
        else:
            break


def start(device_ids):
    with active_line() as serial:
        for device_id in device_ids:
            expected_response = "start logging.*" + REMOTE_RESPONSE_END
            serial_request(
                serial,
                "#{0}StartNow".format(device_id),
                expected_response,
                timeout=10,
            )


def stop(device_ids):
    with active_line() as serial:
        for device_id in device_ids:
            expected_response = "logging stopped.*" + REMOTE_RESPONSE_END
            serial_request(
                serial, "#{0}Stop".format(device_id), expected_response, timeout=10
            )


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
                device_id, chunk_start, chunk_end, SEABIRD_DATA_DIR
            )
            if not os.path.exists(filepath):
                write_chunk(get_sample_range(serial, i, i + chunk_size), filepath)
            else:
                logger.debug(
                    "Chunk found, skipping: {0}, {1}:{2}".format(
                        device_id, chunk_start, chunk_end
                    )
                )


def get_sample_range(serial, device_id, begin, end):
    raw = serial_request(
        serial, "#{0}DD{1},{2}".format(device_id, begin, end), RESPONSE_END, timeout=10
    )
    samples = parse_samples(raw)

    return samples


def parse_samples(raw):
    pattern = "(?P<data>.*)" + re.escape("<Executed/>\r\n")
    match = re.search(pattern, raw, flags=re.DOTALL)

    _, values = match.group("data").strip().split("\r\n\r\n")
    values = [[el.strip() for el in row.split(",")] for row in values.split("\r\n")]
    samples = [
        SeabirdSample(
            timestamp=datetime.strptime(" ".join(row[4:6]), "%d %b %Y %H:%M:%S"),
            **dict((key, row[i]) for i, key in enumerate(DATA_KEYS[1:]))
        )
        for row in values
    ]

    return samples
