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
)
from honcho.core import (
    aquadopp,
    camera,
    cr1000x,
    dts,
    binex,
    upload,
    seabird,
    solar,
    vaisala,
    orders,
    monitor,
)


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


def load_winter_schedule(scheduler):
    scheduler.every().hour.at(":49").do(monitor.execute)

    # scheduler.every().day.at("05:10").do(binex.execute)
    # scheduler.every().day.at("11:10").do(binex.execute)
    # scheduler.every().day.at("17:10").do(binex.execute)
    scheduler.every().day.at("23:10").do(binex.execute)

    # scheduler.every().day.at("04:10").do(camera.execute)
    # scheduler.every().day.at("12:10").do(camera.execute)
    scheduler.every().day.at("20:10").do(camera.execute)

    scheduler.every().hour.at(":57").do(vaisala.execute)

    scheduler.every().hour.at(":50").do(seabird.execute)
    scheduler.every().hour.at(":52").do(aquadopp.execute)

    scheduler.every().hour.at(":55").do(cr1000x.execute)

    scheduler.every().hour.at(":56").do(solar.execute)

    # scheduler.every().day.at("03:05").do(dts.execute)
    # scheduler.every().day.at("07:05").do(dts.execute)
    # scheduler.every().day.at("11:05").do(dts.execute)
    # scheduler.every().day.at("15:05").do(dts.execute)
    # scheduler.every().day.at("19:05").do(dts.execute)
    # scheduler.every().day.at("23:05").do(dts.execute)
    scheduler.every().day.at("21:05").do(dts.execute)

    scheduler.every().day.at("06:10").do(upload.execute)
    scheduler.every().day.at("12:10").do(upload.execute)
    scheduler.every().day.at("18:10").do(upload.execute)
    scheduler.every().day.at("00:10").do(upload.execute)

    scheduler.every().day.at("00:00").do(orders.execute)


def load_summer_schedule(scheduler):
    scheduler.every().hour.at(":49").do(monitor.execute)

    scheduler.every().day.at("05:10").do(binex.execute)
    scheduler.every().day.at("11:10").do(binex.execute)
    scheduler.every().day.at("17:10").do(binex.execute)
    scheduler.every().day.at("23:10").do(binex.execute)

    scheduler.every().day.at("04:10").do(camera.execute)
    scheduler.every().day.at("12:10").do(camera.execute)
    scheduler.every().day.at("20:10").do(camera.execute)

    scheduler.every().hour.at(":57").do(vaisala.execute)

    scheduler.every().hour.at(":50").do(seabird.execute)
    scheduler.every().hour.at(":52").do(aquadopp.execute)

    scheduler.every().hour.at(":55").do(cr1000x.execute)
    scheduler.every().hour.at(":56").do(solar.execute)

    scheduler.every().day.at("03:05").do(dts.execute)
    scheduler.every().day.at("07:05").do(dts.execute)
    scheduler.every().day.at("11:05").do(dts.execute)
    scheduler.every().day.at("15:05").do(dts.execute)
    scheduler.every().day.at("19:05").do(dts.execute)
    scheduler.every().day.at("23:05").do(dts.execute)

    scheduler.every().day.at("06:10").do(upload.execute)
    scheduler.every().day.at("12:10").do(upload.execute)
    scheduler.every().day.at("18:10").do(upload.execute)
    scheduler.every().day.at("00:10").do(upload.execute)

    scheduler.every().day.at("00:00").do(orders.execute)


def load_test_schedule(scheduler):
    scheduler.every().day.at("00:00").do(monitor.execute)
    scheduler.every().day.at("01:00").do(binex.execute)
    scheduler.every().day.at("02:00").do(vaisala.execute)
    scheduler.every().day.at("03:00").do(camera.execute)
    scheduler.every().day.at("04:00").do(seabird.execute)
    scheduler.every().day.at("05:00").do(aquadopp.execute)
    scheduler.every().day.at("06:00").do(cr1000x.execute)
    scheduler.every().day.at("07:00").do(solar.execute)
    scheduler.every().day.at("08:00").do(dts.execute)
    scheduler.every().day.at("09:00").do(upload.execute)
    scheduler.every().day.at("10:00").do(orders.execute)


def execute():
    init_logging()

    name = select_schedule(datetime.now())
    logger.info('Running schedule: {0}'.format(name))
    scheduler = Scheduler()

    if name == SCHEDULE_NAMES.WINTER:
        load_winter_schedule(scheduler)
    if name == SCHEDULE_NAMES.SUMMER:
        load_summer_schedule(scheduler)
    if name == SCHEDULE_NAMES.TEST:
        load_test_schedule(scheduler)
    if name == SCHEDULE_NAMES.SAFE:
        logger.info('No schedule to run in safe mode')
    else:
        raise Exception('No schedule: {0}'.format(name))

    if name == SCHEDULE_NAMES.TEST:
        scheduler.run_all()
    else:
        while True:
            scheduler.run_pending()
            sleep(SCHEDULE_SLEEP)


if __name__ == '__main__':
    execute()
