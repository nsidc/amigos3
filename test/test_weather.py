import os
from datetime import datetime
from time import sleep

import pytest

import honcho.tasks.weather as weather


@pytest.fixture
def weather_mock(mocker, serial_mock):
    outputs = [
        (
            '0R0,Dm=192D,Sm=8.0M,Ta=-1.1C,Ua=65.5P,Pa=986.8H,Rc=0.00M,Rd=0s,Ri=0.0M,'
            'Hc=0.0M,Hd=0s,Hi=0.0M,Rp=0.0M,Hp=0.0M,Th=-1.1C,Vh=0.0N,Vs=11.8V\n'
        ),
        (
            '0R0,Dm=189D,Sm=9.4M,Ta=-1.1C,Ua=65.5P,Pa=986.9H,Rc=0.00M,Rd=0s,Ri=0.0M,'
            'Hc=0.0M,Hd=0s,Hi=0.0M,Rp=0.0M,Hp=0.0M,Th=-1.1C,Vh=0.0N,Vs=11.8V\n'
        ),
    ]

    def weather_listener(port):
        i = 0
        while True:
            os.write(port, outputs[i % len(outputs)])
            sleep(5)
            i += 1

    with serial_mock(listener=weather_listener, baud=9600) as serial:
        yield serial


def test_get_samples(weather_mock, mocker):
    datetime_mock = mocker.MagicMock()
    datetime_mock.now.return_value = datetime(2019, 12, 1, 0, 0, 0)
    mocker.patch('honcho.tasks.weather.powered', mocker.stub())
    mocker.patch('honcho.tasks.weather.datetime', datetime_mock)
    mocker.patch('honcho.tasks.weather.Serial', lambda p, b: weather_mock)

    expected_samples = [
        weather.WeatherSample(
            timestamp=datetime(2019, 12, 1, 0, 0, 0),
            wind_direction=189,
            wind_speed=9.4,
            temperature=-1.1,
            humidity=65.5,
            pressure=986.9,
            rain_accumulation=0.00,
            rain_duration=0,
            rain_intensity=0.0,
            rain_peak_intensity=0.0,
            hail_accumulation=0.0,
            hail_duration=0,
            hail_intensity=0.0,
            hail_peak_intensity=0.0,
            heater_temperature=-1.1,
            heater_voltage=0.0,
            supply_voltage=11.8,
        ),
        weather.WeatherSample(
            timestamp=datetime(2019, 12, 1, 0, 0, 0),
            wind_direction=192,
            wind_speed=8.0,
            temperature=-1.1,
            humidity=65.5,
            pressure=986.8,
            rain_accumulation=0.00,
            rain_duration=0,
            rain_intensity=0.0,
            rain_peak_intensity=0.0,
            hail_accumulation=0.0,
            hail_duration=0,
            hail_intensity=0.0,
            hail_peak_intensity=0.0,
            heater_temperature=-1.1,
            heater_voltage=0.0,
            supply_voltage=11.8,
        ),
    ]
    samples = weather.get_samples(n=2)
    assert set(samples) == set(expected_samples)


@pytest.mark.skip  # broken - task run before mocked
def test_execute_smoke(weather_mock, mocker):
    log_serialized = mocker.MagicMock()
    queue_sbd = mocker.MagicMock()
    mocker.patch('honcho.tasks.weather.powered', mocker.stub())
    mocker.patch('honcho.tasks.weather.log_serialized', log_serialized)
    mocker.patch('honcho.tasks.weather.queue_sbd', queue_sbd)
    mocker.patch('honcho.tasks.weather.task', lambda f: f)

    weather.execute()
