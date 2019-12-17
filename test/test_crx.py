from datetime import datetime
from contextlib import contextmanager

import pytest

from honcho.config import DATA_TAGS
import honcho.tasks.crx as crx


@pytest.fixture
def crx_mock(mocker):
    @contextmanager
    def mock():
        device = mocker.MagicMock()
        device.get_data.return_value = [
            dict(
                [
                    (u'Datetime', datetime(2019, 12, 14, 22, 54, 30)),
                    (u'RecNbr', 178),
                    (u'R6', -1000506.4375),
                    (u'TCDT', 'nan'),
                    (u'T4_5', -248754.609375),
                    (u'T2_5', -259087.578125),
                    (u'R10', -994463.5625),
                    (u'R2_5', -989970.9375),
                    (u'T40', -257977.546875),
                    (u'R6_5', -949568.5),
                    (u'R8_5', -950658.4375),
                    (u'T8_5', -248122.328125),
                    (u'Q', 'nan'),
                    (u'T6', -258624.5625),
                    (u'T6_5', -248710.578125),
                    (u'T10', -258036.5625),
                    (u'R40', -994812.3125),
                    (u'Batt_volt', 0.0),
                    (u'T20', -248824.390625),
                    (u'R4_5', -951115.1875),
                    (u'Ptemp_C', 20.85284423828125),
                    (u'DT', 'nan'),
                    (u'R20', -954313.5),
                ]
            )
        ]

        yield device

    yield mock


def test_execute_smoke(crx_mock, mocker):
    log_serialized = mocker.MagicMock()
    queue_sbd = mocker.MagicMock()
    mocker.patch('honcho.tasks.crx.sleep', mocker.stub())
    mocker.patch('honcho.tasks.crx.powered', mocker.stub())
    mocker.patch('honcho.tasks.crx.connection', crx_mock)
    mocker.patch('honcho.tasks.crx.log_serialized', log_serialized)
    mocker.patch('honcho.tasks.crx.queue_sbd', queue_sbd)

    expected_sample = crx.CRXSample(
        timestamp=datetime(2019, 12, 14, 22, 54, 30),
        RecNbr=178,
        R6=-1000506.4375,
        TCDT='nan',
        T4_5=-248754.609375,
        T2_5=-259087.578125,
        R10=-994463.5625,
        R2_5=-989970.9375,
        T40=-257977.546875,
        R6_5=-949568.5,
        R8_5=-950658.4375,
        T8_5=-248122.328125,
        Q='nan',
        T6=-258624.5625,
        T6_5=-248710.578125,
        T10=-258036.5625,
        R40=-994812.3125,
        Batt_volt=0.0,
        T20=-248824.390625,
        R4_5=-951115.1875,
        Ptemp_C=20.85284423828125,
        DT='nan',
        R20=-954313.5,
    )
    assert crx.get_last_sample() == expected_sample
    # Assert correct data logged
    assert log_serialized.called_once_with(expected_serialized, DATA_TAGS.CRX)
    # Assert correct data queued for sbd
