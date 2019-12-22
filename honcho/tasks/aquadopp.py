import re
from datetime import datetime
from logging import getLogger
from collections import namedtuple

from honcho.config import UNIT, DATA_TAGS, TIMESTAMP_FMT
from honcho.core.imm import active_line, imm_components, REMOTE_RESPONSE_END
import honcho.core.data as data

from honcho.tasks.sbd import queue_sbd
from honcho.util import serial_request
from honcho.tasks.common import task

logger = getLogger(__name__)

_DATA_KEYS = (
    'timestamp',
    'device_id',
    'unknown1',
    'unknown2',
    'error',
    'status',
    'east_vel',
    'north_vel',
    'up_vel',
    'east_ampl',
    'north_ampl',
    'up_ampl',
    'voltage',
    'sound_speeD',
    'heading',
    'pitch',
    'roll',
    'pressure',
    'temperaturE',
    'analogue1',
    'analogue2',
    'speed',
    'direction',
)
DATA_KEYS = namedtuple('DATA_KEYS', (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
CONVERSION_TO_VALUE = {
    DATA_KEYS.ERROR: int,
    DATA_KEYS.STATUS: int,
    DATA_KEYS.UNKNOWN1: int,
    DATA_KEYS.UNKNOWN2: int,
    DATA_KEYS.EAST_VEL: float,
    DATA_KEYS.NORTH_VEL: float,
    DATA_KEYS.UP_VEL: float,
    DATA_KEYS.EAST_AMPL: int,
    DATA_KEYS.NORTH_AMPL: int,
    DATA_KEYS.UP_AMPL: int,
    DATA_KEYS.VOLTAGE: float,
    DATA_KEYS.SOUND_SPEED: float,
    DATA_KEYS.HEADING: float,
    DATA_KEYS.PITCH: float,
    DATA_KEYS.ROLL: float,
    DATA_KEYS.PRESSURE: float,
    DATA_KEYS.TEMPERATURE: float,
    DATA_KEYS.ANALOGUE1: int,
    DATA_KEYS.ANALOGUE2: int,
    DATA_KEYS.SPEED: float,
    DATA_KEYS.DIRECTION: float,
}
CONVERSION_TO_STRING = {
    DATA_KEYS.TIMESTAMP: '{0:' + TIMESTAMP_FMT + '}',
    DATA_KEYS.DEVICE_ID: '{0}',
    DATA_KEYS.ERROR: '{0:d}',
    DATA_KEYS.STATUS: '{0:d}',
    DATA_KEYS.UNKNOWN1: '{0:d}',
    DATA_KEYS.UNKNOWN2: '{0:d}',
    DATA_KEYS.EAST_VEL: '{0:.3f}',
    DATA_KEYS.NORTH_VEL: '{0:.3f}',
    DATA_KEYS.UP_VEL: '{0:.3f}',
    DATA_KEYS.EAST_AMPL: '{0:d}',
    DATA_KEYS.NORTH_AMPL: '{0:d}',
    DATA_KEYS.UP_AMPL: '{0:d}',
    DATA_KEYS.VOLTAGE: '{0:.3f}',
    DATA_KEYS.SOUND_SPEED: '{0:.1f}',
    DATA_KEYS.HEADING: '{0:.1f}',
    DATA_KEYS.PITCH: '{0:.1f}',
    DATA_KEYS.ROLL: '{0:.1f}',
    DATA_KEYS.PRESSURE: '{0:.3f}',
    DATA_KEYS.TEMPERATURE: '{0:.2f}',
    DATA_KEYS.ANALOGUE1: '{0:d}',
    DATA_KEYS.ANALOGUE2: '{0:d}',
    DATA_KEYS.SPEED: '{0:.3f}',
    DATA_KEYS.DIRECTION: '{0:.1f}',
}
AquadoppSample = namedtuple('AquadoppSample', DATA_KEYS)


def query_last_sample(serial, device_id):
    expected_response = re.escape('</SampleData>\r\n') + REMOTE_RESPONSE_END
    raw = serial_request(
        serial, '!{0}SampleGetLast'.format(device_id), expected_response, timeout=5
    )

    return raw


def query_sample_list(serial, device_id):
    expected_response = re.escape('</SampleList>\r\n') + REMOTE_RESPONSE_END
    raw = serial_request(
        serial, '!{0}SampleGetList'.format(device_id), expected_response, timeout=5
    )

    return raw


def query_sample(serial, device_id, sample_id):
    expected_response = re.escape('</SampleData>\r\n') + REMOTE_RESPONSE_END
    raw = serial_request(
        serial,
        '!{0}SampleGetData:{1}'.format(device_id, sample_id),
        expected_response,
        timeout=5,
    )

    return raw


def parse_sample(device_id, raw):
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
    values = match.group('data').strip().split()

    timestamp = datetime.strptime(' '.join(values[:4]), '%m %d %Y %H')
    sample = AquadoppSample(
        timestamp=timestamp,
        device_id=device_id,
        **dict(
            (key, CONVERSION_TO_VALUE[key](values[4 + i]))
            for i, key in enumerate(DATA_KEYS[2:])
        )
    )

    return sample


def parse_sample_list(raw):
    list_pattern = (
        re.escape('<SampleList>') + '(?P<list>.*)' + re.escape('</SampleList>')
    )
    id_pattern = r" ID='(?P<id>.*?)' "

    match = re.search(list_pattern, raw, flags=re.DOTALL)

    sample_list = match.group('list').strip().split('\r\n')
    ids = [re.search(id_pattern, sample).groupdict()['id'] for sample in sample_list]

    return ids


def get_recent_samples(device_ids, n=1):
    samples = []
    with imm_components():
        with active_line() as serial:
            for device_id in device_ids:
                if n == 1:
                    raw = query_last_sample(serial, device_id)
                    samples.append(parse_sample(device_id, raw))
                else:
                    raw = query_sample_list(serial, device_id)
                    sample_list = parse_sample_list(raw)
                    for sample_id in sample_list[-n:]:
                        raw = query_sample(serial, device_id, sample_id)
                        samples.append(parse_sample(device_id, raw))

    return samples


def print_samples(samples):
    data.print_samples(samples, CONVERSION_TO_STRING)


@task
def execute():
    samples = get_recent_samples(UNIT.AQUADOPP_IDS)
    for sample in samples:
        serialized = data.serialize(sample, CONVERSION_TO_STRING)
        data.log_serialized(serialized, DATA_TAGS.AQD)
        queue_sbd(serialized, DATA_TAGS.AQD)
