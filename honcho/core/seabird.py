import re
from datetime import datetime
from logging import getLogger

from serial import Serial

from honcho.config import units
from honcho.core.gpio import disable_serial, enable_serial, imm_off, imm_on
from honcho.core.imm import force_capture_line, power_on, send_wakeup_tone
from honcho.util import serial_request

logger = getLogger(__name__)


def query_seabird(serial, device_id, samples=6):
    expected = re.escape(
        '#{0}DN{1}\r\n'.format(device_id, samples)
        + '<RemoteReply>.*<Executed/>\r\n</RemoteReply>\r\n'
        '<Executed/>\r\n'
        'IMM>'
    )
    raw = serial_request(
        serial, '#{0}DN{1}'.format(device_id, samples), expected, timeout=10
    )

    return raw


def parse_seabird(raw):
    pattern = (
        r'#(?P<device_id>\d{2})DN(?P<samples>\d+)'
        + re.escape('\r\n')
        + re.escape('<RemoteReply>')
        + '(?P<data>.*)'
        + re.escape('<Executed/>\r\n</RemoteReply>')
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    header, data = match.group('data').strip().split('\r\n\r\n')
    header = [[el.strip() for el in row.split('=')] for row in header.split('\r\n')]
    data = [[el.strip() for el in row.split(',')] for row in data.split('\r\n')]
    for i, row in enumerate(data):
        timestamp = datetime.strptime(' '.join(row[3:]), '%d %b %Y %H:%M:%S')
        data[i] = [timestamp] + [float(el) for el in row[:3]]

    start_time = (datetime.strptime(header['start_time'], '%d %b %Y %H:%M:%S'),)
    metadata = {
        'id': match.group('device_id'),
        'samples': match.group('samples'),
        'start_time': start_time,
    }

    return metadata, data


def get_seabird_average(device_id, samples=6):
    imm_on()
    enable_serial()

    serial = Serial('/dev/ttyS4', 9600)
    power_on(serial)
    with force_capture_line(serial):
        send_wakeup_tone(serial)
        raw = query_seabird(serial, device_id, samples=samples)
    serial.close()

    disable_serial()
    imm_off()

    metadata, data = parse_seabird(raw)

    cols = zip(*data)
    delta_mins = round(max(cols[0]) - min(cols[0]).seconds / 60.0)
    averaged_data = [metadata['start_time'], delta_mins]
    n = len(data)
    for col in cols[1:]:
        averaged_data.append(sum(col) / n)

    return averaged_data


if __name__ == '__main__':
    import pdb

    pdb.set_trace()
    get_seabird_average(units.amigos3c.seabird_ids[0])
