import re
from datetime import datetime
from logging import getLogger
from contextlib import closing

from serial import Serial

from honcho.config import IMM_PORT, IMM_BAUD, UNIT, DATA_TAGS
from honcho.core.imm import (
    force_capture_line,
    power_on,
    send_wakeup_tone,
    imm_components,
)
from honcho.tasks.sbd import queue_sbd
from honcho.core.imm import serialize, log_data
from honcho.util import (
    serial_request,
    fail_gracefully,
    log_execution,
)

logger = getLogger(__name__)


def query_samples(serial, device_id, samples=6):
    expected = (
        re.escape('<RemoteReply>')
        + '.*'
        + re.escape('<Executed/>\r\n</RemoteReply>\r\n<Executed/>\r\n')
    )
    raw = serial_request(
        serial, '#{0}DN{1}'.format(device_id, samples), expected, timeout=10
    )

    return raw


def query_status(serial, device_id):
    expected = (
        re.escape('<RemoteReply>')
        + '.*'
        + re.escape('<Executed/>\r\n</RemoteReply>\r\n<Executed/>\r\n')
    )
    raw = serial_request(serial, '#{0}GetSD'.format(device_id), expected, timeout=10)

    return raw


def parse_samples(raw):
    pattern = (
        re.escape('<RemoteReply>')
        + '(?P<data>.*)'
        + re.escape('<Executed/>\r\n</RemoteReply>')
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    header, values = match.group('data').strip().split('\r\n\r\n')
    header = dict([el.strip() for el in row.split('=')] for row in header.split('\r\n'))
    values = [[el.strip() for el in row.split(',')] for row in values.split('\r\n')]
    samples = [
        {
            'timestamp': datetime.strptime(' '.join(row[3:-1]), '%d %b %Y %H:%M:%S'),
            'temperature': row[1],
            'conductivity': row[2],
            'pressure': row[3],
        }
        for row in values
    ]

    start_time = datetime.strptime(header['start time'], '%d %b %Y %H:%M:%S')
    metadata = {
        'start_time': start_time,
    }

    return metadata, samples


def parse_status(raw):
    pattern = (
        re.escape('<RemoteReply>')
        + re.escape('<StatusData')
        + r".*SerialNumber='(?P<serial>\d+)'"
        + re.escape('>')
        + re.escape('<DateTime>')
        + '(?P<DateTime>.*)'
        + re.escape('</DateTime>')
        + re.escape('<vMain>')
        + '(?P<vMain>.*)'
        + re.escape('</vMain>')
        + re.escape('<vLith>')
        + '(?P<vLith>.*)'
        + re.escape('</vLith>')
        + re.escape('<Executed/>\r\n</RemoteReply>')
    )
    match = re.search(pattern, raw)

    return match.groupdict()


def get_recent_samples(device_ids, samples=6):
    samples_by_id = {}
    with imm_components():
        with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
            power_on(serial)
            with force_capture_line(serial):
                for device_id in device_ids:
                    raw = query_samples(serial, device_id, samples)
                    _, samples = parse_samples(raw)
                    samples_by_id[device_id] = samples

    return samples_by_id


def print_samples(samples):
    keys = list(samples)
    print('\t'.join(keys))
    for sample in samples:
        print('\t'.join([sample[key] for key in keys]))


def get_averaged_sample(device_id, samples=6):
    with imm_components():
        with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
            power_on(serial)
            with force_capture_line(serial):
                raw = query_samples(serial, device_id, samples=samples)

    metadata, samples = parse_samples(raw)

    combined = {key: [sample[key] for sample in samples] for key in samples[0]}
    averaged = {key: sum(values) / len(values) for key, values in combined}

    return metadata, averaged


@fail_gracefully
@log_execution
def execute():
    for ID in UNIT.SEABIRD_IDS:
        data = get_averaged_sample(ID)
        logger.debug('Seabird data (ID: {0}): {1}'.format(ID, data))
        serialized = serialize(data, ID)
        log_data(serialized, DATA_TAGS.SBD)
        queue_sbd(DATA_TAGS.SBD, serialized)


if __name__ == '__main__':
    execute()
