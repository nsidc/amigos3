from datetime import datetime
from contextlib import contextmanager

import pytest

from honcho.config import DATA_TAGS, LOG_DIR
import honcho.tasks.crx as crx


@pytest.fixture(autouse=True)
def skip_sleep(mocker):
    mocker.patch('honcho.tasks.crx.sleep', mocker.stub())


@pytest.fixture
def crx_mock(mocker):
    @contextmanager
    def mock():
        device = mocker.MagicMock()
        device.get_raw_packets.return_value = [
            {
                u'IsOffset': 0,
                u'TableName': 'Public',
                u'ByteOffset': None,
                u'BegRecNbr': 72,
                u'RecFrag': [
                    {
                        u'Fields': {
                            'R6': 2114009.25,
                            'TCDT': 1.8759797811508179,
                            'T4_5': 554794.5,
                            'T2_5': 550943.6875,
                            'R10': 2148551.0,
                            'R2_5': 2114220.0,
                            'T40': 577030.25,
                            'R6_5': 2175887.25,
                            'R8_5': 2115781.5,
                            'T8_5': 552317.1875,
                            'Q': 188.0,
                            'T6': 550730.1875,
                            'T6_5': 567382.3125,
                            'T10': 561539.25,
                            'R40': 2199553.75,
                            'Batt_volt': 11.758176803588867,
                            'T20': 550818.3125,
                            'R4_5': 2123721.75,
                            'Ptemp_C': -3.467041015625,
                            'DT': 1.8880000114440918,
                            'R20': 2098787.25,
                        },
                        u'RecNbr': 72,
                        u'TimeOfRec': datetime(2019, 12, 23, 1, 28, 7),
                    }
                ],
                u'TableNbr': 6,
                u'NbrOfRecs': 1,
            }
        ]

        yield device

    yield mock


def test_get_last_sample(crx_mock, mocker):
    log_serialized = mocker.MagicMock()
    queue_sbd = mocker.MagicMock()
    mocker.patch('honcho.tasks.crx.sleep', mocker.stub())
    mocker.patch('honcho.tasks.crx.powered', mocker.stub())
    mocker.patch('honcho.tasks.crx.connection', crx_mock)
    mocker.patch('honcho.tasks.crx.log_serialized', log_serialized)
    mocker.patch('honcho.tasks.crx.queue_sbd', queue_sbd)

    expected_sample = crx.CRXSample(
        timestamp=datetime(2019, 12, 23, 1, 28, 7),
        R6=2114009.25,
        TCDT=1.8759797811508179,
        T4_5=554794.5,
        T2_5=550943.6875,
        R10=2148551.0,
        R2_5=2114220.0,
        T40=577030.25,
        R6_5=2175887.25,
        R8_5=2115781.5,
        T8_5=552317.1875,
        Q=188.0,
        T6=550730.1875,
        T6_5=567382.3125,
        T10=561539.25,
        R40=2199553.75,
        Batt_volt=11.758176803588867,
        T20=550818.3125,
        R4_5=2123721.75,
        Ptemp_C=-3.467041015625,
        DT=1.8880000114440918,
        R20=2098787.25,
    )
    expected_serialized = (
        '2019-12-14T22:54:30,178,0.000,20.853,-1000506.4375,-994463.5625,'
        '-954313.5000,-994812.3125,-989970.9375,-951115.1875,-949568.5000,'
        '-950658.4375,-258624.562500,-258036.562500,-248824.390625,-257977.546875,'
        '-259087.578125,-248754.609375,-248710.578125,-248122.328125,nan,nan,nan'
    )
    assert crx.get_last_sample() == expected_sample
    # Assert correct data logged
    assert log_serialized.called_once_with(expected_serialized, DATA_TAGS.CRX)
    # Assert correct data queued for sbd
    assert queue_sbd.called_once_with(expected_serialized, DATA_TAGS.CRX)


def test_execute_smoke(fs, crx_mock, mocker):
    log_serialized = mocker.MagicMock()
    queue_sbd = mocker.MagicMock()
    mocker.patch('honcho.tasks.crx.sleep', mocker.stub())
    mocker.patch('honcho.tasks.crx.powered', mocker.stub())
    mocker.patch('honcho.tasks.crx.connection', crx_mock)
    mocker.patch('honcho.tasks.crx.log_serialized', log_serialized)
    mocker.patch('honcho.tasks.crx.queue_sbd', queue_sbd)
    mocker.patch('honcho.tasks.crx.task', lambda f: f)

    fs.makedirs(LOG_DIR)
    crx.execute()
