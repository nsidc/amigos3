from datetime import datetime

from schedule.schedule import Scheduler

from honcho.core.sched import (
    select_schedule,
    load_winter_schedule,
    load_summer_schedule,
    load_test_schedule,
)
from honcho.config import SCHEDULE_START_TIMES, SCHEDULE_NAMES


def test_select_schedule():
    # Check winter schedule start
    date = datetime(
        year=2019,
        month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]['month'],
        day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]['day'],
    )
    assert select_schedule(date) == SCHEDULE_NAMES.WINTER

    # Check summer schedule start
    date = datetime(
        year=2019,
        month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]['month'],
        day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]['day'],
    )
    assert select_schedule(date) == SCHEDULE_NAMES.SUMMER

    # Check year start is summer
    date = datetime(year=2019, month=1, day=1)
    assert select_schedule(date) == SCHEDULE_NAMES.SUMMER

    # Check year end is summer
    date = datetime(year=2019, month=12, day=31)
    assert select_schedule(date) == SCHEDULE_NAMES.SUMMER


def test_smoke_load_winter():
    scheduler = Scheduler()
    load_winter_schedule(scheduler)


def test_smoke_load_summer():
    scheduler = Scheduler()
    load_summer_schedule(scheduler)


def test_smoke_load_test():
    scheduler = Scheduler()
    load_test_schedule(scheduler)
