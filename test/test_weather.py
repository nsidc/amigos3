import os
from datetime import datetime
from contextlib import contextmanager
from time import sleep

import pytest

from honcho.config import DATA_TAGS
import honcho.tasks.weather as weather


@pytest.fixture
def wxt_mock(mocker, serial_mock):
    outputs = ['16 Dec 2019 19:21:53']

    def wxt_listener(port):
        i = 0
        while 1:
            sleep(30)
            os.write(port, outputs[i % len(outputs)])
            i += 1

    with serial_mock(listener=wxt_listener, baud=9600) as serial:
        yield serial


@pytest.mark.skip
def test_execute(wxt_mock, mocker):
    log_serialized = mocker.MagicMock()
    queue_sbd = mocker.MagicMock()
    mocker.patch('honcho.tasks.crx.powered', mocker.stub())
    mocker.patch('honcho.tasks.crx.log_serialized', log_serialized)
    mocker.patch('honcho.tasks.crx.queue_sbd', queue_sbd)

    expected_samples = [
        weather.WeatherSample(timestamp=datetime(2019, 12, 14, 22, 54, 30))
    ]  # TODO
    expected_serialized = None
    assert weather.get_samples(n=12) == expected_samples
    # Assert correct data logged
    assert log_serialized.called_once_with(expected_serialized, DATA_TAGS.WXT)
    # Assert correct data queued for sbd
    assert queue_sbd.called_once_with(expected_serialized, DATA_TAGS.WXT)
