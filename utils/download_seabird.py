import argparse
import os
import logging
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime
from time import sleep, time
from contextlib import closing, contextmanager

from serial import Serial

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TIMESTAMP_FMT = '%Y-%m-%dT%H:%M:%S'
DATA_DIR = 'seabird_data'
CHUNK_DIR = os.path.join([DATA_DIR, 'chunks'])

DEFAULT_PORT = '/dev/ttyUSB0'
DEFAULT_BAUD = 9600
IMM_STARTUP_WAIT = 5
IMM_SHUTDOWN_WAIT = 20
IMM_COMMAND_TIMEOUT = 30
RESPONSE_END = re.escape('<Executed/>')
REMOTE_RESPONSE_END = (
    re.escape("<Executed/>") + r"\s*" + re.escape("</RemoteReply>\r\n")
)

_DATA_KEYS = (
    'timestamp',
    'conductivity',
    'temperature',
    'pressure',
    'salinity',
)
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
SeabirdSample = namedtuple('SeabirdSample', DATA_KEYS)


def init_parsers():
    common_parser = argparse.ArgumentParser(prog="honcho", add_help=False)

    common_parser.add_argument(
        "--log-level",
        help="Set logging level (DEBUG, INFO, ERROR)",
        action="store",
        default=None,
        choices=("DEBUG", "INFO", "ERROR"),
    )
    common_parser.add_argument(
        "--device-id",
        help="Set device-id for seabird to access (e.g. 05, 06, 07, 08, 09 or 80)",
        action="store",
        default=None,
    )
    common_parser.add_argument(
        "--port",
        help="Set port for serial connection to IMM",
        action="store",
        default=DEFAULT_PORT,
    )
    common_parser.add_argument(
        "--baud",
        help="Set baud rate for serial connection to IMM",
        action="store",
        default=DEFAULT_BAUD,
    )

    parser = argparse.ArgumentParser(parents=[common_parser])
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    return parser, subparsers


def status_handler(args):
    with active_line(args.port, args.baud) as serial:
        get_status(serial, args.device_id)


def add_status_parser(subparsers):
    parser = subparsers.add_parser("status")
    parser.set_defaults(handler=status_handler)


def pull_handler(args):
    pull_samples(device_id=args.device_id,
                 start=args.start,
                 end=args.end,
                 chunk_size=args.chunk_size,
                 port=args.port,
                 baud=args.baud)


def add_pull_parser(subparsers):
    parser = subparsers.add_parser("pull")
    parser.set_defaults(handler=status_handler)

    parser.add_argument(
        "--start",
        help="Set starting sample to pull (default = first)",
        action="store",
        default=None,
    )
    parser.add_argument(
        "--end",
        help="Set end sample to pull (default = last)",
        action="store",
        default=None,
    )


@contextmanager
def power(serial):
    try:
        serial_request(serial, "\r\nPwrOn", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)
        yield
    finally:
        serial_request(serial, "\r\nPwrOff", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)
        sleep(IMM_SHUTDOWN_WAIT)


@contextmanager
def force_capture_line(serial):
    try:
        serial_request(
            serial, "ForceCaptureLine", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT
        )
        yield
    finally:
        serial_request(serial, "ReleaseLine", RESPONSE_END, timeout=IMM_COMMAND_TIMEOUT)


@contextmanager
def active_line(port=DEFAULT_PORT, baud=DEFAULT_BAUD):
    with closing(Serial(port, baud)) as serial:
        with power(serial):
            with force_capture_line(serial):
                sleep(IMM_STARTUP_WAIT)
                yield serial


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


def console_handler(args):
    console(port=args.port, baud=args.baud)


def add_console_parser(subparsers):
    parser = subparsers.add_parser("console")
    parser.set_defaults(handler=console_handler)


def console(port=DEFAULT_PORT, baud=DEFAULT_BAUD):
    with active_line(port, baud) as serial:
        print('Interactive console to IMM modem')
        print('Enter "quit" or "q" to quit')
        while True:
            print(serial.read(serial.inWaiting()))
            cmd = raw_input("> ")
            if cmd.lower() in ["quit", "q"]:
                break
            serial.write(cmd + "\r\n")
            sleep(1)
            print(serial.read(serial.inWaiting()))
            sleep(3)


def serial_request(serial, command, expected_regex='.+', timeout=10, poll=1):
    if not command.endswith('\r\n'):
        command += '\r\n'

    logger.debug('Sending command to {0}: {1}'.format(serial.port, command.strip()))
    serial.flushInput()
    sleep(1)
    serial.write(command)
    sleep(1)
    start_time = time()
    response = ''
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
            'Response collected from serial at timeout: {0}'.format(response.strip())
        )
        raise Exception('Timed out waiting for expected serial response')

    logger.debug('Response collected from serial: {0}'.format(response))

    return response


def get_status(serial, device_id):
    raw = serial_request(serial,
                         '#{0}GetSD'.format(device_id),
                         RESPONSE_END,
                         timeout=10)
    xml_like = re.search(
        re.escape('<StatusData>') + r'.*' + re.escape('</StatusData>'),
        raw,
        flags=re.DOTALL,
    ).group(0)

    status_data = ET.fromstring(xml_like)
    status = status_data.attrib
    status['datetime'] = datetime.strptime(
        status_data.find('DateTime').text, '%Y-%m-%dT%H:%M:%S'
    )
    status['voltage'] = float(status_data.find('Power/vMain').text)
    status['voltage_li'] = float(status_data.find('Power/vLith').text)
    status['bytes'] = int(status_data.find('MemorySummary/Bytes').text)
    status['samples'] = int(status_data.find('MemorySummary/Samples').text)
    status['samples_free'] = int(status_data.find('MemorySummary/SamplesFree').text)
    status['samples_length'] = int(status_data.find('MemorySummary/SampleLength').text)
    status['sampling'] = status_data.find('AutonomousSampling').text

    return status


def get_sample_range(serial, device_id, begin, end):
    raw = serial_request(serial,
                         '#{0}DD{1},{2}'.format(device_id, begin, end),
                         RESPONSE_END,
                         timeout=10)
    samples = parse_samples(raw)

    return samples


def parse_samples(raw):
    pattern = '(?P<data>.*)' + re.escape('<Executed/>\r\n')
    match = re.search(pattern, raw, flags=re.DOTALL)

    _, values = match.group('data').strip().split('\r\n\r\n')
    values = [[el.strip() for el in row.split(',')] for row in values.split('\r\n')]
    samples = [
        SeabirdSample(
            timestamp=datetime.strptime(' '.join(row[4:6]), '%d %b %Y %H:%M:%S'),
            **dict((key, row[i]) for i, key in enumerate(DATA_KEYS[1:]))
        )
        for row in values
    ]

    return samples


def pull_samples(device_id,
                 start=None,
                 end=None,
                 chunk_size=100,
                 port=DEFAULT_PORT,
                 baud=DEFAULT_BAUD):
    '''
    Get samples for 'device_id' in range 'start' to 'end' in chunks and write to
    'CHUNK_DIR'.

    Chunks already stored will be skipped.
    '''
    with active_line(port, baud) as serial:
        if start is None:
            start = 1
        if end is None:
            status = get_status(serial, device_id)
            end = status['samples']

        chunk_start = start - (start % chunk_size)
        chunk_end = end - (end % chunk_size) + chunk_size

        wait_for_comms(serial)
        for i in range(chunk_start, chunk_end, chunk_size):
            if not os.path.exists(chunk_filepath(device_id, chunk_start, chunk_end)):
                write_chunk(get_sample_range(serial, i, i + chunk_size))
            else:
                logger.debug('Chunk found, skipping: {0}, {1}:{2}'.format(
                    device_id, chunk_start, chunk_end))


def wait_for_comms(serial):
    '''
    Check for status response on serial IMM connection
    '''
    while True:
        try:
            get_status(serial)
        except:  # noqa
            logger.debug('No response to GetSD, fiddle with cable and ill try again...')
            sleep(10)
        else:
            break


def chunk_filepath(device_id, start, end):
    return os.path.join([CHUNK_DIR, device_id, '{0}_{1}.csv'.format(start, end)])


def write_chunk(chunk, filepath):
    '''
    Write chunk of samples as csv to filepath
    '''
    os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'w') as f:
        for sample in chunk:
            f.write(
                ','.join([sample.timestamp.strftime(TIMESTAMP_FMT)] + list(sample[1:]))
                + '\n'
            )

    logger.debug('{0} samples saved to {1}'.format(len(chunk), filepath))


if __name__ == "__main__":
    parser, subparsers = init_parsers()
    add_status_parser(subparsers)
    add_pull_parser(subparsers)
    add_console_parser(subparsers)
    args = parser.parse_args()

    if hasattr(args, "callbacks"):
        for callback in args.callbacks:
            callback()

    if hasattr(args, "handler"):
        args.handler(args)
