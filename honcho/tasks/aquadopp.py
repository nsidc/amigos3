import re
from datetime import datetime
from logging import getLogger
from collections import namedtuple

from honcho.config import UNIT, DATA_TAGS, SEP
from honcho.core.imm import active_line, imm_components, REMOTE_RESPONSE_END
from honcho.core.data import log_data

from honcho.tasks.sbd import queue_sbd
from honcho.util import (
    serial_request,
    fail_gracefully,
    log_execution,
    serialize_datetime,
    deserialize_datetime,
)

logger = getLogger(__name__)

_DATA_KEYS = (
    'TIMESTAMP',
    'DEVICE_ID',
    'ERROR',
    'STATUS',
    'UNKNOWN1',
    'UNKNOWN2',
    'EAST_VEL',
    'NORTH_VEL',
    'UP_VEL',
    'EAST_AMPL',
    'NORTH_AMPL',
    'UP_AMPL',
    'VOLTAGE',
    'SOUND_SPEED',
    'HEADING',
    'PITCH',
    'ROLL',
    'PRESSURE',
    'TEMPERATURE',
    'ANALOGUE1',
    'ANALOGUE2',
    'SPEED',
    'DIRECTION',
)
_VALUE_KEYS = _DATA_KEYS[2:]
DATA_KEYS = namedtuple('DATA_KEYS', _DATA_KEYS)(*_DATA_KEYS)
VALUE_KEYS = namedtuple('VALUE_KEYS', _VALUE_KEYS)(*_VALUE_KEYS)
VALUE_CONVERSIONS = {
    VALUE_KEYS.ERROR: int,
    VALUE_KEYS.STATUS: int,
    VALUE_KEYS.UNKNOWN1: int,
    VALUE_KEYS.UNKNOWN2: int,
    VALUE_KEYS.EAST_VEL: float,
    VALUE_KEYS.NORTH_VEL: float,
    VALUE_KEYS.UP_VEL: float,
    VALUE_KEYS.EAST_AMPL: int,
    VALUE_KEYS.NORTH_AMPL: int,
    VALUE_KEYS.UP_AMPL: int,
    VALUE_KEYS.VOLTAGE: float,
    VALUE_KEYS.SOUND_SPEED: float,
    VALUE_KEYS.HEADING: float,
    VALUE_KEYS.PITCH: float,
    VALUE_KEYS.ROLL: float,
    VALUE_KEYS.PRESSURE: float,
    VALUE_KEYS.TEMPERATURE: float,
    VALUE_KEYS.ANALOGUE1: int,
    VALUE_KEYS.ANALOGUE2: int,
    VALUE_KEYS.SPEED: float,
    VALUE_KEYS.DIRECTION: float,
}
STRING_CONVERSIONS = {
    VALUE_KEYS.ERROR: '{0:d}',
    VALUE_KEYS.STATUS: '{0:d}',
    VALUE_KEYS.UNKNOWN1: '{0:d}',
    VALUE_KEYS.UNKNOWN2: '{0:d}',
    VALUE_KEYS.EAST_VEL: '{0:.3f}',
    VALUE_KEYS.NORTH_VEL: '{0:.3f}',
    VALUE_KEYS.UP_VEL: '{0:.3f}',
    VALUE_KEYS.EAST_AMPL: '{0:d}',
    VALUE_KEYS.NORTH_AMPL: '{0:d}',
    VALUE_KEYS.UP_AMPL: '{0:d}',
    VALUE_KEYS.VOLTAGE: '{0:.3f}',
    VALUE_KEYS.SOUND_SPEED: '{0:.1f}',
    VALUE_KEYS.HEADING: '{0:.1f}',
    VALUE_KEYS.PITCH: '{0:.1f}',
    VALUE_KEYS.ROLL: '{0:.1f}',
    VALUE_KEYS.PRESSURE: '{0:.3f}',
    VALUE_KEYS.TEMPERATURE: '{0:.2f}',
    VALUE_KEYS.ANALOGUE1: '{0:d}',
    VALUE_KEYS.ANALOGUE2: '{0:d}',
    VALUE_KEYS.SPEED: '{0:.3f}',
    VALUE_KEYS.DIRECTION: '{0:.1f}',
}
SAMPLE = namedtuple('SAMPLE', DATA_KEYS)


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
    sample = SAMPLE(
        TIMESTAMP=timestamp,
        DEVICE_ID=device_id,
        **dict(
            (key, VALUE_CONVERSIONS[key](values[4 + i]))
            for i, key in enumerate(VALUE_KEYS)
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


def serialize(sample):
    serialized = SEP.join(
        [serialize_datetime(sample.TIMESTAMP), sample.DEVICE_ID]
        + [STRING_CONVERSIONS[key].format(getattr(sample, key)) for key in VALUE_KEYS]
    )

    return serialized


def deserialize(serialized):
    split = serialized.split(SEP)

    deserialized = SAMPLE(
        TIMESTAMP=deserialize_datetime(split[0]),
        DEVICE_ID=split[1],
        **dict(
            (key, VALUE_CONVERSIONS[key](split[2 + i]))
            for i, key in enumerate(VALUE_KEYS)
        )
    )

    return deserialized


def print_samples(samples):
    print(', '.join(DATA_KEYS))
    print('-' * 80)
    for sample in samples:
        print(serialize(sample).replace(SEP, ', '))


@fail_gracefully
@log_execution
def execute():
    samples = get_recent_samples(UNIT.AQUADOPP_IDS)
    for sample in samples:
        serialized = serialize(sample)
        log_data(serialized, DATA_TAGS.AQD)
        queue_sbd(DATA_TAGS.AQD, serialized)


if __name__ == '__main__':
    execute()
