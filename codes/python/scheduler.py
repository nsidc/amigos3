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
from monitor import get_schedule_health, put_to_power_sleep, put_to_inactive_sleep, clear_cached, get_system_performance, has_slept, reschedule, get_stat
from iridium import sbd as sb, dial
from dts import test as dts_test

# call("env >> /media/mmcblk0p1/logs/system.log", shell=True)
welcome()
printf("The state of the schedule so far is presented in the table below.", date=True)
get_stat()
g = gps_data()
g.update_time(out=True)


class summer():
    def __init__(self, *args, **kwargs):
        self.sched_summer = schedule.Scheduler()  # create a new schedule instance

    def vaisala_schedule(self):
        from vaisala import Average_Reading as vg
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_summer.every().hour.at(":59").do(v.vaisala)  # add vaisala schedule

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_summer.every().day.at("05:10").do(gps.get_binex)
        self.sched_summer.every().day.at("11:10").do(gps.get_binex)
        self.sched_summer.every().day.at("17:10").do(gps.get_binex)
        self.sched_summer.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        cam = ptz()
        self.sched_summer.every().day.at("04:10").do(cam.move)
        self.sched_summer.every().day.at("10:10").do(cam.move)
        self.sched_summer.every().day.at("16:10").do(cam.move)
        self.sched_summer.every().day.at("22:10").do(cam.move)

    def aquadopp_schedule(self):
        from aquadopp import amigos_box_sort_AQ
        self.sched_summer.every().hour.at(":52").do(amigos_box_sort_AQ)

    def seabird_schedule(self):
        from seabird import amigos_box_sort_SB
        self.sched_summer.every().hour.at(":51").do(amigos_box_sort_SB)

    def cr100x_schedule(self):
        # add cr100 schedules
        from cr1000x import cr1000x
        cr = cr1000x()
        self.sched_summer.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        from solar import readsolar
        self.sched_summer.every().hour.at(":57").do(readsolar)

    def dial_out(self):
        d = dial()
        unit = amigos_Unit()
        # # box a
        if unit == "A":
            self.sched_summer.every().day.at("06:10").do(d.Out)
            self.sched_summer.every().day.at("12:10").do(d.Out)
            self.sched_summer.every().day.at("18:10").do(d.Out)
            self.sched_summer.every().day.at("00:10").do(d.Out)
        # # box b
        elif unit == "B":
            self.sched_summer.every().day.at("06:20").do(d.Out)
            self.sched_summer.every().day.at("12:20").do(d.Out)
            self.sched_summer.every().day.at("18:20").do(d.Out)
            self.sched_summer.every().day.at("00:20").do(d.Out)
        # # box c
        elif unit == "C":
            self.sched_summer.every().day.at("06:30").do(d.Out)
            self.sched_summer.every().day.at("12:30").do(d.Out)
            self.sched_summer.every().day.at("18:30").do(d.Out)
            self.sched_summer.every().day.at("00:30").do(d.Out)

    def dial_in(self):
        d = dial()
        self.sched_summer.every().day.at("19:20").do(d.In)

    def dts(self):
        self.sched_summer.every().day.at("03:05").do(dts_test)
        self.sched_summer.every().day.at("09:05").do(dts_test)
        self.sched_summer.every().day.at("15:05").do(dts_test)
        self.sched_summer.every().day.at("21:05").do(dts_test)

    def sbd(self):
        # box A
        s = sb()
        unit = amigos_Unit()
        if unit == "A":
            self.sched_summer.every().day.at("00:02").do(s.SBD)
        # # box B
        elif unit == "B":
            self.sched_summer.every().day.at("00:04").do(s.SBD)
        # # box C
        elif unit == "C":
            self.sched_summer.every().day.at("00:06").do(s.SBD)

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
        return self.sched_summer  # return the new loaded schedule


class winter():
    def __init__(self):
        self.sched_winter = schedule.Scheduler()

    def vaisala_schedule(self):
        from vaisala import Average_Reading as vg
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_winter.every().hour.at(":59").do(v.vaisala)

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
        self.sched_winter.every().hour.at(":51").do(amigos_box_sort_SB)

    def cr100x_schedule(self):
        # add cr100x schedules
        from cr1000x import cr1000x
        cr = cr1000x()
        self.sched_winter.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        from solar import readsolar
        self.sched_winter.every().hour.at(":56").do(readsolar)

    def dial_out(self):
        d = dial()
        unit = amigos_Unit()

        # # box a
        if unit == "A":
            self.sched_winter.every().day.at("00:10").do(d.Out)
        # # box b
        elif unit == "B":
            self.sched_winter.every().day.at("00:20").do(d.Out)
        # # box c
        elif unit == "C":
            self.sched_winter.every().day.at("00:30").do(d.Out)

    def dial_in(self):

        d = dial()
        self.sched_winter.every().day.at("19:20").do(d.In)

    def dts(self):
        self.sched_winter.every().day.at("21:05").do(dts_test)

    def sbd(self):
        s = sb()
        unit = amigos_Unit()
        if unit == "A":
            self.sched_winter.every().day.at("00:02").do(s.SBD)
            # # box B
        elif unit == "B":
            self.sched_winter.every().day.at("00:04").do(s.SBD)
            # # box C
        elif unit == "C":
            self.sched_winter.every().day.at("00:06").do(s.SBD)

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
        self.health()
        # self.voltage()
        self.execute()
        self.onboard_device()
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
    # winter_time = {'start': {'day': 1,
    #                          'month': 5},
    #                'end': {'day': 31,
    #                        'month': 8}
    #                }
    winter_time = {'start': {'day': 1,
                             'month': 5},
                   'end': {'day': 1,
                           'month': 8}
                   }
    # summer time frame
    # summer_time = {'start': {'day': 1,
    #                          'month': 9},
    #                'end': {'day': 30,
    #                        'month': 4}
    #                }
    summer_time = {'start': {'day': 2,
                             'month': 8},
                   'end': {'day': 30,
                           'month': 4}
                   }
    return winter_time, summer_time


def run_schedule():
    # winter time frame
    winter_time, summer_time = season()
    # track thw rumming schedule
    winter_running = False
    summer_running = False
    # create a summer and winter schedule
    s = summer()
    w = winter()
    m = monitor()
    summer_task = s.sched()
    winter_task = w.sched()
    monitor_task = m.sched()
    # run forever
    while True:
        if has_slept():
            printf("Amigos! Wakes up! Job(s) awaiting.")
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
            printf("Checking for voltage level.")
            put_to_power_sleep()
            printf("All ready for task(s) execution!")
        new_sched = get_schedule()
        if new_sched:
            winter_time = new_sched[0]
            summer_time = new_sched[0]
        if not is_on_checker(1, 6):
            modem_on(1)
        # get the today date (tritron time must update to uptc time)
        today = datetime.now()
        # minutes = today.minute
        # hours = today.hour
        # create datetime instance of winter and summer bracket
        winter_start = today.replace(
            month=winter_time['start']['month'], day=winter_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        winter_end = today.replace(
            month=winter_time['end']['month'], day=winter_time['end']['day'], hour=23, minute=59, second=59, microsecond=0)
        # summer_start = today.replace(
        #     month=summer_time['start']['month'], day=summer_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        # summer_end = today.replace(
        #     month=summer_time['end']['month'], day=summer_time['end']['day'], hour=23, minute=59, second=59, microsecond=0)
        monitor_task.run_pending()
        # check if today falls into summer
        # print(winter_start, winter_end, summer_start, summer_end)
        if winter_start <= today < winter_end:
            if not winter_running:
                winter_running = True
                printf('Loading winter schedule')
                w = winter()
                winter_task = w.sched()
                sleep(10)
                printf("clearing summer tasks")
                summer_task.clear()
                # winter_task.run_pending()
                summer_running = False
                printf('Started winter schedule')
            winter_task.run_pending()
            if not is_on_checker(1, 6):
                modem_on(1)
            reschedule(jobs=winter_task.jobs)
            put_to_inactive_sleep(winter_task.jobs)
        else:
            # do nothing if schedule is already running. This to avoid reloading the schedule arasing saved schedule
            if not summer_running:
                summer_running = True  # set flag
                printf('Loading summer schedule')
                s = summer()  # reload the schedule
                summer_task = s.sched()
                # summer_task.run_pending()
                sleep(10)
                printf("clearing winter tasks")
                winter_task.clear()
                winter_running = False
                printf('Started summer schedule')
            summer_task.run_pending()
            if not is_on_checker(1, 6):
                modem_on(1)
            reschedule(jobs=summer_task.jobs)
            put_to_inactive_sleep(summer_task.jobs)

        # check if today falls into winter
        sleep(1)

 # if winter_running:
        #     winter_task.run_pending()
        #     reschedule(jobs=winter_task.jobs)
        #     if not is_on_checker(1, 6):
        #         modem_on(1)
        #     # with open('/media/mmcblk0p1/logs/schedule.log', 'w+') as sched_log:
        #     #     sched_log.write(str(sorted(winter_task.jobs)))
        #     if int(hours) == 00 and int(minutes) == 15:
        #         winter_running = False
        #         printf('Loading summer schedule')
        #         s = summer()  # reload the schedule
        #         summer_task = s.sched()
        #         sleep(61)
        #         printf('clearing winter schedule')
        #         winter_task.clear()
        #         printf('Started summer schedule')
        #         summer_running = True  # set flag
        #     put_to_inactive_sleep(winter_task.jobs)
        # elif summer_running:
        #     summer_task.run_pending()
        #     reschedule(jobs=summer_task.jobs)
        #     if not is_on_checker(1, 6):
        #         modem_on(1)
        #     # with open('/media/mmcblk0p1/logs/schedule.log', 'w+') as sched_log:
        #     #     sched_log.write(str(sorted(summer_task.jobs)))
        #     if int(hours) == 00 and int(minutes) == 15:
        #         summer_running = False  # set flag
        #         printf('Loading winter schedule')
        #         s = winter()  # reload the schedule
        #         winter_task = s.sched()
        #         sleep(61)
        #         printf("clearing summer tasks")
        #         summer_task.clear()
        #         printf('Started winter schedule')
        #         winter_running = True
        #     put_to_inactive_sleep(summer_task.jobs)

        # else:
        #     printf('Loading summer schedule')
        #     sleep(2)
        #     summer_running = True
        #     printf('Started summer schedule as default')


# running this script start the schedule
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
# t = cold_test()
        # s = t.sched()
        # dog = dog_mode(mode=1)
        # dog.run_all()
        # mo = monitor()
        # m = mo.sched()
        # while True:
        #     m.run_pending()
        #     dog.run_pending()
        #     s.run_pending()
        #     with open('/media/mmcblk0p1/logs/sched.log', 'w+') as sched_log:
        #         sched_log.write(str(m.jobs)+',' + str(s.jobs))
        #     sleep(1)
