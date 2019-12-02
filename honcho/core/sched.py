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
)
from honcho.tasks import import_task


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


def execute():
    init_logging()

    name = select_schedule(datetime.now())
    logger.info('Running schedule: {0}'.format(name))
    scheduler = Scheduler()

    if name == SCHEDULE_NAMES.SAFE:
        logger.info('No schedule to run in safe mode')
        return
    else:
        load_schedule(scheduler, SCHEDULES[name])

    if name == SCHEDULE_NAMES.TEST:
        scheduler.run_all()
    else:
        while True:
            scheduler.run_pending()
            sleep(SCHEDULE_SLEEP)


if __name__ == '__main__':
    execute()
