import logging
import os
import re
from time import sleep, time

logger = logging.getLogger(__name__)

TIMESTAMP_FMT = "%Y-%m-%dT%H:%M:%S"


def serial_request(serial, command, expected_regex=".+", timeout=10, poll=1):
    if not command.endswith("\r\n"):
        command += "\r\n"

    logger.debug("Sending command to {0}: {1}".format(serial.port, command.strip()))
    serial.flushInput()
    sleep(1)
    serial.write(command)
    sleep(1)
    start_time = time()
    response = ""
    response_length = len(response)
    while time() - start_time < timeout:
        response += serial.read(serial.inWaiting())
        if re.search(expected_regex, response, flags=re.DOTALL):
            break

        new_response_length = len(response)
        if new_response_length > response_length:
            start_time = time()
            response_length = new_response_length

        sleep(poll)
    else:
        logger.debug(
            "Response collected from serial at timeout: {0}".format(response.strip())
        )
        raise Exception("Timed out waiting for expected serial response")

    logger.debug("Response collected from serial: {0}".format(response))

    return response


def chunk_filepath(device_id, start, end, chunk_dir):
    return os.path.join([chunk_dir, device_id, "{0}_{1}".format(start, end)])


def write_chunk(chunk, filepath):
    """
    Write chunk of samples to filepath
    """
    os.makedirs(os.path.dirname(filepath))

    with open(filepath, "w") as f:
        for sample in chunk:
            f.write(
                ",".join([sample.timestamp.strftime(TIMESTAMP_FMT)] + list(sample[1:]))
                + "\n"
            )

    logger.debug("{0} samples saved to {1}".format(len(chunk), filepath))
