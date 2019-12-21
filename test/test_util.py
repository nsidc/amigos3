from datetime import datetime

from honcho.util import average_datetimes


def test_average_datetimes():
    datetimes = [
        datetime(2019, 10, 1, 12, 0, 0),
        datetime(2019, 10, 1, 13, 0, 0),
        datetime(2019, 10, 1, 15, 0, 0),
        datetime(2019, 10, 1, 16, 0, 0),
    ]
    expected = datetime(2019, 10, 1, 14, 0, 0)

    assert average_datetimes(datetimes) == expected
