import re
from datetime import datetime
from logging import getLogger

from serial import Serial

from honcho.config import units
from honcho.core.gpio import disable_serial, enable_serial, imm_off, imm_on
from honcho.core.imm import force_capture_line, power_on, send_wakeup_tone
from honcho.util import serial_request

logger = getLogger(__name__)


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

    serial = Serial('/dev/ttyS4', 9600)
    power_on(serial)
    with force_capture_line(serial):
        send_wakeup_tone(serial)
        raw = query_aquadopp(serial, device_id)
    serial.close()

    disable_serial()
    imm_off()

    metadata, data = parse_aquadopp(raw)

    return metadata, data


if __name__ == '__main__':
    import pdb

    pdb.set_trace()
    get_aquadopp(units.amigos3a.aquadopp_ids[0])
