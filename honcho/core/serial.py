import re
from logging import getLogger
from time import sleep, time

logger = getLogger(__name__)


def serial_request(serial, command, expected_regex='.+', timeout=10, poll=1):
    if not command.endswith('\r\n'):
        command += '\r\n'

    logger.debug('Sending command to {0}: {1}'.format(serial.port, command))
    serial.write(command)
    start_time = time.time()
    response = ''
    while time() - start_time < timeout:
        response += serial.read(serial.inWaiting())
        if re.match(expected_regex, response):
            break
        sleep(poll)
    else:
        logger.debug('Response collected from serial at timeout: {0}'.format(response))
        raise Exception('Timed out waiting for expected serial response')

    logger.debug('Response collected from serial: {0}'.format(response))

    return response
