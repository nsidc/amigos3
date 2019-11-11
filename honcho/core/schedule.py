import signal
from datetime import datetime
from time import sleep

import honcho.config as cfg
import horcho.core.iridium as iridium
from honcho.core import (aquadopp, camera, cr1000x, dts, gps, iridium, seabird, solar,
                         vaisala)
from schedule.schedule import Scheduler

SCHEDULE_SLEEP = 30


def select_schedule(date):
    for sched_change in cfg.schedule_times:
        start = datetime(
            year=date.year, month=sched_change['month'], day=sched_change['day']
        )
        if date >= start:
            return sched_change["name"]
    else:
        return sched_change["name"]


def load_winter_schedule(scheduler):
    # scheduler.every().day.at("05:10").do(gps.collect_binex)
    # scheduler.every().day.at("11:10").do(gps.collect_binex)
    # scheduler.every().day.at("17:10").do(gps.collect_binex)
    scheduler.every().day.at("23:10").do(gps.collect_binex)

    scheduler.every().hour.at(":57").do(vaisala.collect)

    # scheduler.every().day.at("04:10").do(camera.collect)
    # scheduler.every().day.at("12:10").do(camera.collect)
    scheduler.every().day.at("20:10").do(camera.collect)

    scheduler.every().hour.at(":50").do(seabird.collect)
    scheduler.every().hour.at(":52").do(aquadopp.collect)

    scheduler.every().hour.at(":55").do(cr1000x.collect)

    scheduler.every().hour.at(":56").do(solar.collect)

    # scheduler.every().day.at("03:05").do(dts.collect)
    # scheduler.every().day.at("07:05").do(dts.collect)
    # scheduler.every().day.at("11:05").do(dts.collect)
    # scheduler.every().day.at("15:05").do(dts.collect)
    # scheduler.every().day.at("19:05").do(dts.collect)
    # scheduler.every().day.at("23:05").do(dts.collect)
    scheduler.every().day.at("21:05").do(dts.collect)

    scheduler.every().day.at("06:10").do(iridium.upload_pending)
    scheduler.every().day.at("12:10").do(iridium.upload_pending)
    scheduler.every().day.at("18:10").do(iridium.upload_pending)
    scheduler.every().day.at("00:10").do(iridium.upload_pending)


def load_summer_schedule(scheduler):
    scheduler.every().hour.at(":49").do(get_stat_log)

    scheduler.every().day.at("05:10").do(gps.collect_binex)
    scheduler.every().day.at("11:10").do(gps.collect_binex)
    scheduler.every().day.at("17:10").do(gps.collect_binex)
    scheduler.every().day.at("23:10").do(gps.collect_binex)

    scheduler.every().hour.at(":57").do(vaisala.collect)

    scheduler.every().day.at("04:10").do(camera.collect)
    scheduler.every().day.at("12:10").do(camera.collect)
    scheduler.every().day.at("20:10").do(camera.collect)

    scheduler.every().hour.at(":50").do(seabird.collect)
    scheduler.every().hour.at(":52").do(aquadopp.collect)

    scheduler.every().hour.at(":55").do(cr1000x.collect)
    scheduler.every().hour.at(":56").do(solar.collect)

    scheduler.every().day.at("03:05").do(dts.collect)
    scheduler.every().day.at("07:05").do(dts.collect)
    scheduler.every().day.at("11:05").do(dts.collect)
    scheduler.every().day.at("15:05").do(dts.collect)
    scheduler.every().day.at("19:05").do(dts.collect)
    scheduler.every().day.at("23:05").do(dts.collect)

    scheduler.every().day.at("06:10").do(iridium.upload_pending)
    scheduler.every().day.at("12:10").do(iridium.upload_pending)
    scheduler.every().day.at("18:10").do(iridium.upload_pending)
    scheduler.every().day.at("00:10").do(iridium.upload_pending)


def load_schedule(name, scheduler):
    if name == 'winter':
        load_winter_schedule(scheduler)
    if name == 'summer':
        load_summer_schedule(scheduler)
    else:
        raise Exception('No schedule: {0}'.format(name))


def run():
    schedule_name = select_schedule(datetime.now())
    scheduler = Scheduler()
    load_schedule(schedule_name, scheduler)
    while True:
        scheduler.run_pending()
        sleep(SCHEDULE_SLEEP)


if __name__ == '__main__':
    run()
