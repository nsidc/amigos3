import re
from contextlib import contextmanager
from datetime import datetime
from logging import getLogger

from serial import Serial

from honcho.config import units
from honcho.core.gpio import disable_serial, enable_serial, imm_off, imm_on
from honcho.core.serial import serial_request

logger = getLogger(__name__)


def power_on(serial):
    expected = re.escape('<PowerOn/>\r\nIMM>')
    serial_request(serial, 'PwrOn', expected, timeout=10)


@contextmanager
def force_capture_line(serial):
    try:
        expected = re.escape('ForceCaptureLine\r\n<Executed/>\r\nIMM>')
        serial_request(serial, 'ForceCaptureLine', expected, timeout=5)
        yield
    finally:
        expected = re.escape('ReleaseLine\r\n<Executed/>\r\nIMM>')
        serial_request(serial, 'ReleaseLine', expected, timeout=5)


def send_wakeup_tone(serial):
    expected = re.escape(
        'SendWakeUpTone\r\n' '(<Executing/>\r\n)*' '<Executed/>\r\n' 'IMM>'
    )
    serial_request(serial, 'SendWakeUpTone', expected, timeout=10)


def query_seabird(serial, device_id, samples=6):
    expected = re.escape(
        '#{0}DN{1}\r\n'.format(device_id, samples)
        + '<RemoteReply>.*<Executed/>\r\n</RemoteReply>\r\n'
        '<Executed/>\r\n'
        'IMM>'
    )
    raw = serial_request(
        serial, '#{0}DN{1}'.format(device_id, samples), expected, timeout=5
    )

    return raw


def query_aquadopp(serial, device_id):
    expected = re.escape(
        '!{0}SAMPLEGETLAST\r\n'.format(device_id)
        + '<RemoteReply>.*<Executed/>\r\n</RemoteReply>\r\n'
        '<Executed/>\r\n'
        'IMM>'
    )

    raw = serial_request(
        serial, '!{0}SAMPLEGETLAST'.format(device_id), expected, timeout=5
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


def parse_aquadopp(raw):
    pattern = (
        r'!(?P<device_id>\d{2})SAMPLEGETLAST'
        + re.escape('\r\n')
        + '.*'
        + '<SampleData (?P<metadata>.*)>'
        + '(?P<data>.*)\r\n'
        + '</SampleData>'
    )
    match = re.search(pattern, raw, flags=re.DOTALL)

    # header = dict([el.split('=') for el in match.group('metadata').strip().split()])
    data = match.group('data').strip().split()

    timestamp = datetime.strptime(' '.join(data[:4]), '%m %d %Y %H')
    error, status = data[4:6]
    data = [timestamp] + [float(el) for el in data[6:]]

    metadata = {'error': error, 'status': status, 'id': match.group('device_id')}

    return metadata, data


def get_aquadopp(device_id):
    imm_on()
    enable_serial()

    with Serial('/dev/ttyS4', 9600) as serial:
        power_on(serial)
        with force_capture_line(serial):
            send_wakeup_tone(serial)
            raw = query_aquadopp(serial, device_id)

    disable_serial()
    imm_off()

    metadata, data = parse_aquadopp(raw)

    return metadata, data


def get_seabird_average(device_id, samples=6):
    imm_on()
    enable_serial()

    with Serial('/dev/ttyS4', 9600) as serial:
        power_on(serial)
        with force_capture_line(serial):
            send_wakeup_tone(serial)
            raw = query_seabird(serial, device_id, samples=samples)

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
    get_aquadopp(units.amigos3a.aquadopp_ids[0])
