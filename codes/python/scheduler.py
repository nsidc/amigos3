# # scheduling system

from schedule import schedule
from time import sleep
from datetime import datetime
from gps import gps_data as gps_data
from gpio import modem_on, is_on_checker, all_off
from vaisala import Average_Reading as vg
from onvif import ptz_client as ptz
from cr1000x import cr1000x
from onboard_device import get_humidity, get_temperature
from solar import readsolar
import ast
from execp import printf, sig_handler, terminateProcess, set_reschedule, welcome, amigos_Unit
import signal
import sys
import traceback
from monitor import get_schedule_health, put_to_power_sleep, put_to_inactive_sleep, clear_cached, get_system_performance, has_slept
from iridium import sbd as sb, dial
from dts import test as dts_test
from subprocess import call

# call("env >> /media/mmcblk0p1/logs/system.log", shell=True)
welcome()


class summer():
    def __init__(self, *args, **kwargs):
        self.sched_summer = schedule.Scheduler()  # create a new schedule instance

    def vaisala_schedule(self):
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_summer.every().hour.at(":58").do(v.vaisala)  # add vaisala schedule

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

    def cr100x_schedule(self):
        # add cr100 schedules
        cr = cr1000x()
        self.sched_summer.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        self.sched_summer.every().hour.at(":56").do(readsolar)

    def dial_out(self):
        d = dial()
        # # box a
        if amigos_Unit() == "A":
            self.sched_summer.every().day.at("06:10").do(d.Out)
            self.sched_summer.every().day.at("12:10").do(d.Out)
            self.sched_summer.every().day.at("18:10").do(d.Out)
            self.sched_summer.every().day.at("00:10").do(d.Out)
        # # box b
        elif amigos_Unit() == "B":
            self.sched_summer.every().day.at("06:20").do(d.Out)
            self.sched_summer.every().day.at("12:20").do(d.Out)
            self.sched_summer.every().day.at("18:20").do(d.Out)
            self.sched_summer.every().day.at("00:20").do(d.Out)
        # # box c
        elif amigos_Unit() == "C":
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
        if amigos_Unit() == "A":
            self.sched_summer.every().day.at("00:02").do(s.send)
        # # box B
        elif amigos_Unit() == "B":
            self.sched_summer.every().day.at("00:04").do(s.send)
        # # box C
        elif amigos_Unit() == "C":
            self.sched_summer.every().day.at("00:06").do(s.send)

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
        return self.sched_summer  # return the new loaded schedule


class winter():
    def __init__(self, *args, **kwargs):
        self.sched_winter = schedule.Scheduler()

    def vaisala_schedule(self):
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_winter.every().hour.at(":58").do(v.vaisala)

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_winter.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        cam = ptz()
        self.sched_winter.every().day.at("20:10").do(cam.move)

    def cr100x_schedule(self):
        # add cr100x schedules
        cr = cr1000x()
        self.sched_winter.every().hour.at(":55").do(cr.cr1000)

    def solar_schedule(self):
        self.sched_winter.every().hour.at(":56").do(readsolar)

    def dial_out(self):
        d = dial()
        # # box a
        if amigos_Unit() == "A":
            self.sched_winter.every().day.at("00:10").do(d.Out)
        # # box b
        elif amigos_Unit() == "B":
            self.sched_winter.every().day.at("00:20").do(d.Out)
        # # box c
        elif amigos_Unit() == "C":
            self.sched_winter.every().day.at("00:30").do(d.Out)

    def dial_in(self):

        d = dial()
        self.sched_winter.every().day.at("19:20").do(d.In)

    def dts(self):
        self.sched_winter.every().day.at("21:05").do(dts_test)

    def sbd(self):
<<<<<<< HEAD
        s = sb()
        if amigos_Unit() == "A":
            self.sched_winter.every().day.at("00:02").do(s.send)
        # # box B
        elif amigos_Unit() == "B":
            self.sched_winter.every().day.at("00:04").do(s.send)
        # # box C
        elif amigos_Unit() == "C":
            self.sched_winter.every().day.at("00:06").do(s.send)
=======
        self.sched_winter.every().day.at("00:02").do(sbd_send)
>>>>>>> master

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
def reschedule(jobs):
    """
    Rerun a task that has failed without affecting the integrity of the schedule. update
    """
    track = {"cr1000": [0, 0, "CR100x"],
             "readsolar": [0, 0, "Solar sensor"],
             "vaisala": [0, 0, "Vaisala"],
             "get_binex": [0, 0, "GPS Binex"],
             "Out": [0, 0, "Dial_out"],
             "In": [0, 0, "Dial_in"],
             "IMM": [0, 0, "IMM and Sea Bird"],
             "dts": [0, 0, "DTS"],
             "move": [0, 0, "Camera"]
             }
    try:
        task = None
        with open("/media/mmcblk0p1/logs/reschedule.log", "r") as res:
            task = res.read()
        if task in ["", None, " "]:
            pass
        else:
            for job in jobs:
                total_run = track[job.job_func.__name__][1]
                track[job.job_func.__name__][1] = total_run + \
                    track[job.job_func.__name__][1]
                if track[job.job_func.__name__][0] > 1:
                    track[job.job_func.__name__][0] = 0
                elif job.job_func.__name__ == task:
                    printf("Executing {0} task that failed previously. {1} total rerun :)".format(
                        track[job.job_func.__name__][2], track[job.job_func.__name__][1]))
                    next_second = job.next_run.second
                    next_minute = job.next_run.minute
                    next_hour = job.next_run.hour
                    next_day = job.next_run.day
                    next_month = job.next_run.month
                    next_year = job.next_run.year
                    printf("Schedule integrity will be altered :(")
                    job.run()
                    job.next_run = job.next_run.replace(
                        minute=next_minute, hour=next_hour, day=next_day, year=next_year, second=next_second, month=next_month)
                    set_reschedule("")
                    printf("Done rerunning {0} task. Schedule integrity was restored :)".format(
                        track[job.job_func.__name__][2]))
                    return
    except:
        printf("Rerun failed due to the following error, Might try again :)")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


class monitor():
    def __init__(self, *args, **kwargs):
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
<<<<<<< HEAD
        # self.inactive()
=======
        self.inactive()
>>>>>>> master
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
    winter_time = {'start': {'day': 1,
                             'month': 5},
                   'end': {'day': 31,
                           'month': 8}
                   }
    # summer time frame
    summer_time = {'start': {'day': 1,
                             'month': 9},
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
            mem = get_system_performance()
            printf("System Memory: {0}Kb used ram, {1}Kb free ram, {2}Kb cached , and {3}Kb buffer".format(
                mem[0], mem[1], mem[2], mem[3]))
            if mem[1] < 10000:
                printf("clearing memory and cached too big")
                clear_cached()
                sleep(1)
                mem = get_system_performance()
<<<<<<< HEAD
                printf("System memory after cleanup : {0}Kb used ram, {1}Kb free ram, {2}Kb cached and {3}kb buffer".format(
=======
                printf("System performance after : {0}K used ram, {1}K free ram, {2}K cached and {3}k buffer".format(
>>>>>>> master
                    mem[0], mem[1], mem[2], mem[3]))
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
        minutes = today.minute
        hours = today.hour
        # create datetime instance of winter and summer bracket
        winter_start = today.replace(
            month=winter_time['start']['month'], day=winter_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        winter_end = today.replace(
            month=winter_time['end']['month'], day=winter_time['start']['day'], hour=23, minute=59, second=59, microsecond=0)
        summer_start = today.replace(
            month=summer_time['start']['month'], day=summer_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        summer_end = today.replace(
            month=summer_time['end']['month'], day=summer_time['start']['day'], hour=23, minute=59, second=59, microsecond=0)
        monitor_task.run_pending()
        if winter_running:
            winter_task.run_pending()
            reschedule(winter_task.jobs)
            # with open('/media/mmcblk0p1/logs/schedule.log', 'w+') as sched_log:
            #     sched_log.write(str(sorted(winter_task.jobs)))
            if int(hours) == 00 and int(minutes) == 15:
                winter_running = False
                printf('loading summer schedule')
                s = summer()  # reload the schedule
                summer_task = s.sched()
                sleep(61)
                printf('clearing winter schedule')
                winter_task.clear()
                printf('Started summer schedule')
                summer_running = True  # set flag
            put_to_inactive_sleep(winter_task.jobs)
        elif summer_running:
            summer_task.run_pending()
            reschedule(summer_task.jobs)
            # with open('/media/mmcblk0p1/logs/schedule.log', 'w+') as sched_log:
            #     sched_log.write(str(sorted(summer_task.jobs)))
            if int(hours) == 00 and int(minutes) == 15:
                summer_running = False  # set flag
                printf('loading winter schedule')
                s = winter()  # reload the schedule
                winter_task = s.sched()
                sleep(61)
                printf("clearing summer tasks")
                summer_task.clear()
                printf('Started winter schedule')
                winter_running = True
            put_to_inactive_sleep(summer_task.jobs)

        else:
            printf('loading summer schedule')
            sleep(2)
            summer_running = True
            printf('Started summer schedule as default')

        sleep(1)
        # # check if today falls into summer
        # if summer_start < today <= summer_end:
        #     # do nothing if schedule is already running. This to avoid reloading the schedule arasing saved schedule
        #     if not summer_running:
        #         summer_running = True  # set flag
        #         s = summer()  # reload the schedule
        #         summer_task = s.sched()
        #         summer_task.run_pending()
        #         winter_task.clear()
        #         winter_running = False
        #         print('Started summer sched')
        #     else:
        #         summer_task.run_pending()
        # # check if today falls into winter
        # elif winter_start <= today < winter_end:
        #     if not winter_running:
        #         winter_running = True
        #         w = winter()
        #         summer_task.clear()
        #         winter_task = w.sched()
        #         winter_task.run_pending()
        #         summer_running = False
        #         print('Started winter sched')
        #     else:
        #         winter_task.run_pending()
        # else:
        #     pass
        # sleep(1)


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
