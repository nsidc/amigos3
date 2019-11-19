import re
from datetime import datetime
from logging import getLogger
from contextlib import closing

from serial import Serial

from honcho.config import IMM_PORT, IMM_BAUD
from honcho.core.gpio import powered
from honcho.core.imm import force_capture_line, power_on, send_wakeup_tone
from honcho.util import serial_request, fail_gracefully

logger = getLogger(__name__)


def query(serial, device_id):
    expected = (
        r'!\d{2}SAMPLEGETLAST'
        + re.escape('\r\n')
        + re.escape('<RemoteReply>')
        + '.*'
        + re.escape('<Executed/></RemoteReply>\r\n')
        + re.escape('<Executed/>\r\n')
        + re.escape('IMM>')
    )

    raw = serial_request(
        serial, '!{0}SAMPLEGETLAST'.format(device_id), expected, timeout=5
    )

    return raw


def parse(raw):
    pattern = (
        r'!(?P<device_id>\d{2})SAMPLEGETLAST'
        + re.escape('\r\n')
        + '.*'
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

    metadata = {'error': error, 'status': status, 'id': match.group('device_id')}

    return metadata, data


def get_data(device_id):
    with powered('imm'), powered('ser'):
        with closing(Serial(IMM_PORT, IMM_BAUD)) as serial:
            power_on(serial)
            with force_capture_line(serial):
                send_wakeup_tone(serial)
                raw = query(serial, device_id)

    _, data = parse(raw)

    return data


@fail_gracefully
def execute():
    raise NotImplementedError


if __name__ == '__main__':
    execute()
