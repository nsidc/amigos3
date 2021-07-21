import logging
import re
from time import sleep

from honcho.config import (IRD_DEFAULT_TIMEOUT, SBD_MAX_SIZE, SBD_TRANSMISSION_TIMEOUT,
                           SBD_WRITE_TIMEOUT)
from honcho.util import serial_request

logger = logging.getLogger(__name__)


def ping(serial):
    expected = re.escape("OK\r\n")
    try:
        logger.debug("Pinging iridium")
        serial_request(serial, "AT", expected, timeout=IRD_DEFAULT_TIMEOUT)
    except Exception:
        logger.error("Ping failed")
        raise Exception("Iridium did not respond correctly to ping")
    else:
        logger.debug("Iridium ping ok")


def check_signal(serial):
    expected = re.escape("+CSQ:") + r"(?P<strength>\d)" + re.escape("\r\n")
    try:
        logger.debug("Checking signal")
        response = serial_request(
            serial, "AT+CSQ", expected, timeout=IRD_DEFAULT_TIMEOUT
        )
    except Exception:
        logger.error("Signal check failed")
        raise Exception("Iridium did not respond correctly to signal query")

    strength = int(re.search(expected, response).groupdict()["strength"])
    logger.debug("Signal strength: {0}".format(strength))

    return strength


def message_size(message):
    size = len(message.encode("utf-8"))
    return size


def send_sbd(serial, message):
    clear_mo_buffer(serial)
    sleep(1)

    size = message_size(message)
    assert size <= SBD_MAX_SIZE, "Message is too large: {0} > {1}".format(
        size, SBD_MAX_SIZE
    )

    # Initiate write text
    expected = "READY\r\n"
    serial_request(serial, "AT+SBDWT", expected, timeout=IRD_DEFAULT_TIMEOUT)
    sleep(5)

    # Submit message
    expected = r"(?P<status>\d)" + re.escape("\r\n\r\n") + r"OK" + re.escape("\r\n")
    response = serial_request(serial, message, expected, timeout=SBD_WRITE_TIMEOUT)
    status = int(re.search(expected, response).groupdict()["status"])
    if status:
        raise Exception("SBD write command returned error status")
    sleep(3)

    # Initiate transfer to GSS
    expected = (
        re.escape("+SBDIX: ")
        + (
            r"(?P<mo_status>\d+), "
            r"(?P<momsn>\d+), "
            r"(?P<mt_status>\d+), "
            r"(?P<mtmsn>\d+), "
            r"(?P<mt_length>\d+), "
            r"(?P<mt_queued>\d+)"
        )
        + re.escape("\r\n")
    )
    response = serial_request(
        serial, "AT+SBDIX", expected, timeout=SBD_TRANSMISSION_TIMEOUT
    )
    status = int(re.search(expected, response).groupdict()["mo_status"])
    if status:
        raise Exception("SBD transfer command returned error status")


def clear_mo_buffer(serial):
    logger.debug("Clearing MO buffer")
    expected = r"(?P<status>\d)" + re.escape("\r\n")
    response = serial_request(
        serial, "AT+SBDD0", re.escape("\r\n"), timeout=IRD_DEFAULT_TIMEOUT
    )
    status = int(re.search(expected, response).groupdict()["status"])
    if status:
        raise Exception("SBD clear mo command returned error status")
