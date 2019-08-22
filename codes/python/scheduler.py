# # scheduling system

from schedule import schedule
from time import sleep
from datetime import datetime
from gps import gps_data as gps_data
from gpio import modem_on, is_on_checker, all_off
from onvif import ptz_client as ptz
from onboard_device import get_humidity, get_temperature
import ast
from execp import printf, sig_handler, terminateProcess, welcome, amigos_Unit
import signal
import sys
import traceback
from monitor import get_schedule_health, put_to_power_sleep, put_to_inactive_sleep, has_slept, reschedule, get_stat
from iridium import sbd as sb, dial


param = [False, False, None]


class summer():
    def __init__(self, *args, **kwargs):
        self.sched_summer = schedule.Scheduler()  # create a new schedule instance

    def stat_schedule(self):
        from monitor import get_stat_log
        self.sched_summer.every().hour.at(":49").do(get_stat_log)

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_summer.every().day.at("05:10").do(gps.get_binex)
        self.sched_summer.every().day.at("11:10").do(gps.get_binex)
        self.sched_summer.every().day.at("17:10").do(gps.get_binex)
        self.sched_summer.every().day.at("23:10").do(gps.get_binex)

    def vaisala_schedule(self):
        from vaisala import Average_Reading as vg
        vai = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_summer.every().hour.at(":57").do(vai.vaisala)  # add vaisala schedule

    def camera_schedule(self):
        cam = ptz()
        self.sched_summer.every().day.at("04:10").do(cam.move)
        self.sched_summer.every().day.at("12:10").do(cam.move)
        self.sched_summer.every().day.at("20:10").do(cam.move)

    def aquadopp_schedule(self):
        from aquadopp import amigos_box_sort_AQ
        self.sched_summer.every().hour.at(":52").do(amigos_box_sort_AQ)

    def seabird_schedule(self):
        from seabird import amigos_box_sort_SB
        self.sched_summer.every().hour.at(":50").do(amigos_box_sort_SB)

    def cr100x_schedule(self):
        # add cr100 schedules
        from cr1000x import cr1000x
        cr = cr1000x()
        self.sched_summer.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        from solar import readsolar
        self.sched_summer.every().hour.at(":56").do(readsolar)

    def dial_out(self):
        di = dial()
        unit = amigos_Unit()
        # # box a
        if unit == "A":
            self.sched_summer.every().day.at("06:10").do(di.Out)
            self.sched_summer.every().day.at("12:10").do(di.Out)
            self.sched_summer.every().day.at("18:10").do(di.Out)
            self.sched_summer.every().day.at("00:10").do(di.Out)
        # # box b
        elif unit == "B":
            self.sched_summer.every().day.at("06:20").do(di.Out)
            self.sched_summer.every().day.at("12:20").do(di.Out)
            self.sched_summer.every().day.at("18:20").do(di.Out)
            self.sched_summer.every().day.at("00:20").do(di.Out)
        # # box c
        elif unit == "C":
            self.sched_summer.every().day.at("06:30").do(di.Out)
            self.sched_summer.every().day.at("12:30").do(di.Out)
            self.sched_summer.every().day.at("18:30").do(di.Out)
            self.sched_summer.every().day.at("00:30").do(di.Out)

    def dial_in(self):
        di = dial()
        self.sched_summer.every().day.at("19:20").do(di.In)

    def dts(self):
        from dts import ssh
        self.sched_summer.every().day.at("03:05").do(ssh)
        self.sched_summer.every().day.at("07:05").do(ssh)
        self.sched_summer.every().day.at("11:05").do(ssh)
        self.sched_summer.every().day.at("15:05").do(ssh)
        self.sched_summer.every().day.at("19:05").do(ssh)
        self.sched_summer.every().day.at("23:05").do(ssh)

    def sbd(self):
        # box A
        ss = sb()
        unit = amigos_Unit()
        if unit == "A":
            self.sched_summer.every().day.at("00:02").do(ss.SBD)
        # # box B
        elif unit == "B":
            self.sched_summer.every().day.at("00:04").do(ss.SBD)
        # # box C
        elif unit == "C":
            self.sched_summer.every().day.at("00:06").do(ss.SBD)

    def sched(self):
        # load all the schedules
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        self.solar_schedule()
        self.dial_in()
        self.dial_out()
        self.sbd()
        self.dts()
        self.aquadopp_schedule()
        self.seabird_schedule()
        self.stat_schedule()
        return self.sched_summer  # return the new loaded schedule


class winter():
    def __init__(self):
        self.sched_winter = schedule.Scheduler()

    def stat_schedule(self):
        from monitor import get_stat_log
        self.sched_winter.every().hour.at(":49").do(get_stat_log)

    def vaisala_schedule(self):
        from vaisala import Average_Reading as vg
        vai = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_winter.every().hour.at(":57").do(vai.vaisala)

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_winter.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        cam = ptz()
        self.sched_winter.every().day.at("20:10").do(cam.move)

    def aquadopp_schedule(self):
        from aquadopp import amigos_box_sort_AQ
        self.sched_winter.every().hour.at(":52").do(amigos_box_sort_AQ)

    def seabird_schedule(self):
        from seabird import amigos_box_sort_SB
        self.sched_winter.every().hour.at(":50").do(amigos_box_sort_SB)

    def cr100x_schedule(self):
        # add cr100x schedules
        from cr1000x import cr1000x
        cr = cr1000x()
        self.sched_winter.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        from solar import readsolar
        self.sched_winter.every().hour.at(":56").do(readsolar)

    def dial_out(self):
        di = dial()
        unit = amigos_Unit()

        # # box a
        if unit == "A":
            self.sched_winter.every().day.at("00:10").do(di.Out)
        # # box b
        elif unit == "B":
            self.sched_winter.every().day.at("00:20").do(di.Out)
        # # box c
        elif unit == "C":
            self.sched_winter.every().day.at("00:30").do(di.Out)

    def dial_in(self):

        di = dial()
        self.sched_winter.every().day.at("19:20").do(di.In)

    def dts(self):
        from dts import ssh
        self.sched_winter.every().day.at("21:05").do(ssh)

    def sbd(self):
        ss = sb()
        unit = amigos_Unit()
        if unit == "A":
            self.sched_winter.every().day.at("00:02").do(ss.SBD)
            # # box B
        elif unit == "B":
            self.sched_winter.every().day.at("00:04").do(ss.SBD)
            # # box C
        elif unit == "C":
            self.sched_winter.every().day.at("00:06").do(ss.SBD)

    def sched(self):
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        self.solar_schedule()
        self.dial_in()
        self.dial_out()
        self.dts()
        self.sbd()
        self.seabird_schedule()
        self.aquadopp_schedule()
        self.stat_schedule()
        return self.sched_winter


class monitor():
    def __init__(self):
        self.sched_monitor = schedule.Scheduler()

    def execute(self):
        pass

    def health(self):
        self.sched_monitor.every(15).minutes.at(':13').do(get_schedule_health)

    # def voltage(self):
    #     self.sched_monitor.every(15).minutes.at(":14").do(put_to_power_sleep)

    def onboard_device(self):
        self.sched_monitor.every().minute.at(":30").do(get_humidity)
        self.sched_monitor.every().minute.at(":33").do(get_temperature)

    # def inactive(self):
    #     self.sched_monitor.every().minute.at(":59").do(put_to_inactive_sleep)

    def sched(self):
        # self.health()
        # self.voltage()
        self.execute()
        # self.onboard_device()
        # self.inactive()
        return self.sched_monitor


def get_schedule():
    data = None
    try:
        with open('media/mmcblk0p1/logs/new_schedule.log', 'r') as update:
            data = update.read()
        if data:
            data = data.split(',')
            data[0] = ast.literal_eval(data[0])
            data[1] = ast.literal_eval(data[1])
            if not isinstance(data[0], 'dict') and not isinstance(data[1], 'dict') and not isinstance(data, 'list'):
                return None
            return data[0], data[1]
    except:
        pass
    return None


def signals():
    # register the signals to be caught
    signal.signal(signal.SIGHUP, sig_handler)
    signal.signal(signal.SIGINT, terminateProcess)
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGILL, sig_handler)
    signal.signal(signal.SIGTRAP, sig_handler)
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGBUS, sig_handler)
    signal.signal(signal.SIGFPE, sig_handler)
    # signal.signal(signal.SIGKILL, sig_handler)
    signal.signal(signal.SIGUSR1, sig_handler)
    signal.signal(signal.SIGSEGV, sig_handler)
    signal.signal(signal.SIGUSR2, sig_handler)
    signal.signal(signal.SIGPIPE, sig_handler)
    signal.signal(signal.SIGALRM, sig_handler)
    signal.signal(signal.SIGTERM, terminateProcess)


def season(update=None):
    if update:
        pass
    # # winter time frame
    # winter_time = {'start': {'day': 1,
    #                          'month': 5},
    #                'end': {'day': 31,
    #                        'month': 8}
    #                }
    # # summer time frame
    # summer_time = {'start': {'day': 1,
    #                          'month': 9},
    #                'end': {'day': 30,
    #                        'month': 4}
    #                }
    winter_time = {'start': {'day': 1,
                             'month': 5},
                   'end': {'day': 1,
                           'month': 8}
                   }

    summer_time = {'start': {'day': 2,
                             'month': 8},
                   'end': {'day': 30,
                           'month': 4}
                   }
    return winter_time, summer_time


def run_summer(winter_task, summer_task):
    from dts import get_dts_time
    from monitor import get_restore_schedule
    if not param[1]:
        param[1] = True  # set flag
        printf('Loading summer schedule')
        s = summer()  # reload the schedule
        summer_task = s.sched()
        # summer_task.run_pending()
        sleep(5)
        printf("clearing winter tasks")
        winter_task.clear()
        param[0] = False
        printf('Started summer schedule')
    summer_task.run_pending()
    # if not is_on_checker(1, 6):
    #     modem_on(1)
    reschedule(jobs=summer_task.jobs)
    dts_time = get_dts_time()
    if param[2] == "DTS" and dts_time not in ['\n', '', " "]:
        from monitor import update_dts_time
        update_dts_time(summer_task.jobs)
    get_restore_schedule(summer_task.jobs)
    param[2] = put_to_inactive_sleep(summer_task.jobs)
    # printf(next_job)


def run_winter(winter_task, summer_task):
    from dts import get_dts_time
    from monitor import get_restore_schedule
    if not param[0]:
        param[0] = True
        printf('Loading winter schedule')
        w = winter()
        winter_task = w.sched()
        sleep(5)
        printf("clearing summer tasks")
        summer_task.clear()
        # winter_task.run_pending()
        param[1] = False
        printf('Started winter schedule')
    winter_task.run_pending()
    # if not is_on_checker(1, 6):
    #     modem_on(1)
    reschedule(jobs=winter_task.jobs)
    dts_time = get_dts_time()
    if param[2] == "DTS" and dts_time not in ['\n', '', " ", None]:
        from monitor import update_dts_time
        update_dts_time(winter_task.jobs)
        dts_time = ''
    get_restore_schedule(winter_task.jobs)
    param[2] = put_to_inactive_sleep(winter_task.jobs)


def run_schedule():
    # winter time frame
    winter_time, summer_time = season()
    # track thw rumming schedule
    # create a summer and winter schedule
    s = summer()
    w = winter()
    m = monitor()
    summer_task = s.sched()
    winter_task = w.sched()
    monitor_task = m.sched()
    welcome()
    printf("The state of the schedule so far is presented in the table below.", date=True)
    get_stat()
    g = gps_data()
    g.update_time(out=True)
    # run forever
    while True:
        if has_slept():
            printf("Amigos! Wakes up! Job(s) awaiting.")
            printf("Checking for voltage level.")
            put_to_power_sleep()
            printf("All ready for task(s) execution!")
        new_sched = get_schedule()
        if new_sched:
            winter_time = new_sched[0]
            summer_time = new_sched[0]
        # get the today date (tritron time must update to uptc time)
        today = datetime.now()
        winter_start = today.replace(
            month=winter_time['start']['month'], day=winter_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        winter_end = today.replace(
            month=winter_time['end']['month'], day=winter_time['end']['day'], hour=23, minute=59, second=59, microsecond=0)
        monitor_task.run_pending()
        if winter_start <= today < winter_end:
            run_winter(winter_task, summer_task)
        else:
            run_summer(winter_task, summer_task)
        sleep(1)
        # mem = get_system_performance()
        # printf("System Memory: {0}Kb used ram, {1}Kb free ram, {2}Kb cached , and {3}Kb buffer".format(
        #     mem[0], mem[1], mem[2], mem[3]))
        # if mem[1] < 10000:
        #     printf("Clearing memory and cached too big")
        #     clear_cached()
        #     sleep(1)
        #     mem = get_system_performance()
        #     printf("System memory after cleanup : {0}Kb used ram, {1}Kb free ram, {2}Kb cached and {3}kb buffer".format(
        #         mem[0], mem[1], mem[2], mem[3]))

        # if not is_on_checker(1, 6):
        #     modem_on(1)
        # minutes = today.minute
        # hours = today.hour
        # create datetime instance of winter and summer bracket

        # summer_start = today.replace(
        #     month=summer_time['start']['month'], day=summer_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        # summer_end = today.replace(
        #     month=summer_time['end']['month'], day=summer_time['end']['day'], hour=23, minute=59, second=59, microsecond=0)

        # check if today falls into summer
        # print(winter_start, winter_end, summer_start, summer_end)


# running this script start the schedule (some errors might occur). However the amigos.py in the main directory should be your do go
if __name__ == "__main__":
    try:
        signals()
        modem_on(1)
        run_schedule()
    except Exception as err:
        printf('Scheduler failed with error message :' +
               str(err) + str(sys.exc_info()[0]) + '\n' + 'Trying to restart scheduler')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
