from datetime import datetime
from time import sleep
import logging

from schedule.schedule import Scheduler

from honcho.logs import init_logging
from honcho.config import (
    MODE,
    MODES,
    SCHEDULE_START_TIMES,
    SCHEDULE_SLEEP,
    SCHEDULE_NAMES,
    SCHEDULES,
    MAX_SYSTEM_SLEEP,
    MIN_SYSTEM_VOLTAGE,
)
from honcho.tasks import import_task
from honcho.core.system import system_standby
from honcho.core.onboard import get_voltage


logger = logging.getLogger(__name__)


def select_schedule(date):
    if MODE in (MODES.SAFE, MODES.TEST, MODES.SUMMER, MODES.WINTER):
        return MODE
    elif MODE == MODES.NORMAL:
        winter_start = datetime(
            year=date.year,
            month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]['month'],
            day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]['day'],
        )
        summer_start = datetime(
            year=date.year,
            month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]['month'],
            day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]['day'],
        )
        if (date >= winter_start) and (date < summer_start):
            return SCHEDULE_NAMES.WINTER
        else:
            return SCHEDULE_NAMES.SUMMER
    else:
        raise Exception('Unexpected MODE: {0}'.format(MODE))


def load_schedule(scheduler, config):
    for period, time, task_module in config:
        task = import_task(task_module)
        getattr(scheduler.every(), period).at(time).do(task.execute)


def voltage_check():
    voltage = get_voltage()
    voltage_ok = voltage >= MIN_SYSTEM_VOLTAGE
    if not voltage_ok:
        logger.warning(
            'System voltage {0} supply below minimum {1}'.format(
                voltage, MIN_SYSTEM_VOLTAGE
            )
        )
        system_standby(MAX_SYSTEM_SLEEP)

    return voltage_ok


def idle_check(scheduler):
    idle_minutes = scheduler.idle_seconds / 60.0
    if idle_minutes > 2:
        logger.info('Schedule idle for {0} minutes'.format(idle_minutes))
        system_standby(min(int(idle_minutes - 1), MAX_SYSTEM_SLEEP))


def execute():
    init_logging()

    name = select_schedule(datetime.now())
    logger.info('Running schedule: {0}'.format(name))
    scheduler = Scheduler()

    load_schedule(scheduler, SCHEDULES[name])

    if name == SCHEDULE_NAMES.TEST:
        scheduler.run_all()
    else:
        while True:
            if not voltage_check():
                continue

            scheduler.run_pending()
            idle_check(scheduler)
            sleep(SCHEDULE_SLEEP)


if __name__ == '__main__':
    execute()
