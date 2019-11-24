import re
from datetime import datetime
from logging import getLogger
from contextlib import closing

from serial import Serial

from honcho.config import IMM_PORT, IMM_BAUD, UNIT, DATA_TAGS, DATA_LOG
from honcho.core.gpio import powered
from honcho.core.sbd import queue_sbd
from honcho.core.imm import force_capture_line, power_on, send_wakeup_tone
from honcho.util import (
    serial_request,
    fail_gracefully,
    serialize_datetime,
    deserialize_datetime,
)

logger = getLogger(__name__)


def query(serial, device_id, samples=6):
    expected = (
        '#{0}DN{1}'.format(device_id, samples)
        + re.escape('\r\n')
        + re.escape('<RemoteReply>')
        + '.*'
        + re.escape('<Executed/>\r\n</RemoteReply>\r\n<Executed/>\r\nIMM>')
    )
    raw = serial_request(
        serial, '#{0}DN{1}'.format(device_id, samples), expected, timeout=10
    )

    return raw


def parse(raw):
    pattern = (
        r'#(?P<device_id>\d{2})DN(?P<samples>\d+)'
        + re.escape('\r\n')
        + re.escape('<RemoteReply>')
        + '(?P<data>.*)'
        + re.escape('<Executed/>\r\n</RemoteReply>')
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    header, data = match.group('data').strip().split('\r\n\r\n')
    header = dict([el.strip() for el in row.split('=')] for row in header.split('\r\n'))
    data = [[el.strip() for el in row.split(',')] for row in data.split('\r\n')]
    for i, row in enumerate(data):
        timestamp = datetime.strptime(' '.join(row[3:-1]), '%d %b %Y %H:%M:%S')
        data[i] = [timestamp] + [float(el) for el in row[:3]]

    start_time = datetime.strptime(header['start time'], '%d %b %Y %H:%M:%S')
    metadata = {
        'id': match.group('device_id'),
        'samples': int(match.group('samples')),
        'start_time': start_time,
    }

    return metadata, data


def get_data(device_id, samples=6):
    with powered(['imm', 'ser']):
        with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
            power_on(serial)
            with force_capture_line(serial):
                send_wakeup_tone(serial)
                raw = query(serial, device_id, samples=samples)

    metadata, data = parse(raw)

    cols = list(zip(*data))
    delta_mins = round((max(cols[0]) - min(cols[0])).seconds / 60.0)
    averaged_data = [metadata['start_time'], delta_mins]
    n = len(data)
    for col in cols[1:]:
        averaged_data.append(sum(col) / n)

    return averaged_data


def log_data(s):
    if not s.endswith('\n'):
        s += '\n'

    with open(DATA_LOG(DATA_TAGS.AQD), 'a') as f:
        f.write(s)


def serialize(data):
    serialized = serialize_datetime(data[0]) + ','.join(data)

    return serialized


def deserialize(serialized):
    split = serialized.split(',')

    return [deserialize_datetime(split[0])] + [float(el) for el in split[1:]]


@fail_gracefully
def execute():
    for ID in UNIT.SEABIRD_IDS:
        data = get_data(ID)
        serialized = serialize(data)
        log_data(serialized)
        queue_sbd(DATA_TAGS.SBD, serialized)


if __name__ == '__main__':
    execute()
