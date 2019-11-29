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
    log_data,
    serialize,
)
from honcho.tasks.sbd import queue_sbd
from honcho.util import (
    serial_request,
    fail_gracefully,
    log_execution,
)

logger = getLogger(__name__)


def query_sample(serial, device_id):
    expected = (
        re.escape('<RemoteReply>')
        + '.*'
        + re.escape('<Executed/>')
        + re.escape('</RemoteReply>\r\n')
        + re.escape('<Executed/>\r\n')
    )

    raw = serial_request(
        serial, '!{0}SAMPLEGETLAST'.format(device_id), expected, timeout=5
    )

    return raw


def parse_sample(raw):
    pattern = (
        '.*'
        + re.escape('<SampleData ')
        + '(?P<metadata>.*)'
        + re.escape('>')
        + '(?P<data>.*)'
        + re.escape('\r\n')
        + re.escape('</SampleData>')
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    # header = dict([el.split('=') for el in match.group('metadata').strip().split()])
    data = match.group('data').strip().split()

    timestamp = datetime.strptime(' '.join(data[:4]), '%m %d %Y %H')
    error, status = [int(el) for el in data[4:6]]
    data = [timestamp] + [float(el) for el in data[6:]]

    metadata = {'error': error, 'status': status}

    return metadata, data


def get_data(device_id):
    with imm_components():
        with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
            power_on(serial)
            with force_capture_line(serial):
                send_wakeup_tone(serial)
                raw = query_sample(serial, device_id)

    _, data = parse_sample(raw)

    return data


@fail_gracefully
@log_execution
def execute():
    for ID in UNIT.AQUADOPP_IDS:
        data = get_data(ID)
        serialized = serialize(data, ID)
        log_data(serialized, DATA_TAGS.AQD)
        queue_sbd(DATA_TAGS.AQD, serialized)


if __name__ == '__main__':
    execute()
