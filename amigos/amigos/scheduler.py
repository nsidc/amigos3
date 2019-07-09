# # scheduling system
from schedule import schedule as schedule
from time import sleep
from datetime import datetime
from gps import gps_data as gps_data
from gpio import modem_on
from vaisala import Average_Reading as vg
from onvif.onvif import ptz_client as ptz
from cr1000x import cr1000x as cr1000x
from onboard_device import get_humidity, get_temperature
from solar import readsolar
from watchdog import set_mode as dog_mode
import ast
from execp import printf, sig_handler, terminateProcess
import signal
import sys
import traceback
from monitor import schedule_health
# import monitor as monitor


class cold_test():
    def __init__(self, *args, **kwargs):
        self.sched_test = schedule.Scheduler()  # create a new schedule instance

    def vaisala_schedule(self):
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_test.every().hour.at(":10").do(v.average_data)  # add vaisala schedule

        self.sched_test.every().hour.at(":50").do(v.average_data)  # add vaisala schedule

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_test.every().hour.at(":30").do(gps.get_binex)
        self.sched_test.every().hour.at(":59").do(gps.get_binex)

    def camera_schedule(self):
        cam = ptz()

        self.sched_test.every().hour.at(":45").do(cam.cam_test)
        self.sched_test.every().hour.at(":25").do(cam.cam_test)

    def cr100x_schedule(self):
        # add cr100 schedules
        cr = cr1000x()
        self.sched_test.every().hour.at(":20").do(cr.write_file)
        self.sched_test.every().hour.at(":42").do(cr.write_file)

    def solar_schedule(self):
        self.sched_test.every().hour.at(":15").do(readsolar)
        self.sched_test.every().hour.at(":55").do(readsolar)

    def onboard_device(self):
        self.sched_test.every().minute.do(get_humidity)
        self.sched_test.every().minute.do(get_temperature)

    def sched(self):
        # load all the schedules
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        self.solar_schedule()
        self.onboard_device()
        return self.sched_test  # return the new loaded schedule


class summer():
    def __init__(self, *args, **kwargs):
        self.sched_summer = schedule.Scheduler()  # create a new schedule instance

    def vaisala_schedule(self):
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_summer.every().hour.at(":58").do(v.average_data)  # add vaisala schedule

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_summer.every().day.at("05:10").do(gps.get_binex)
        self.sched_summer.every().day.at("11:10").do(gps.get_binex)
        self.sched_summer.every().day.at("17:10").do(gps.get_binex)
        self.sched_summer.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        pass

    def cr100x_schedule(self):
        # add cr100 schedules
        cr = cr1000x()
        self.sched_summer.every().hour.at(":55").do(cr.write_file)

    def sched(self):
        # load all the schedules
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        return self.sched_summer  # return the new loaded schedule


class winter():
    def __init__(self, *args, **kwargs):
        self.sched_winter = schedule.Scheduler()

    def vaisala_schedule(self):
        v = vg()
        # Perform this measurement reading every hour between :58 to :00
        self.sched_winter.every().hour.at(":58").do(v.average_data)

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_winter.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        pass

    def cr100x_schedule(self):
        # add cr100x schedules
        cr = cr1000x()
        self.sched_winter.every().hour.at(":55").do(cr.write_file)

    def sched(self):
        # load all the winter schedule
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        return self.sched_winter


class monitor():
    def __init__(self, *args, **kwargs):
        self.sched_monitor = schedule.Scheduler()

    def execute(self):
        pass

    def health(self):
        self.sched_monitor.every().hour.at(':28').do(schedule_health)

    def voltage(self):
        pass

    def sched(self):
        self.health()
        return self.sched_monitor


def get_schedule():
    data = None
    try:
        with open('media/mmcblk0p1/amigos/amigos/logs/new_schedule.log', 'r') as update:
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


def run_schedule():
    # winter time frame
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

    # track thw rumming schedule
    winter_running = False
    summer_running = False
    # create a summer and winter schedule
    s = summer()
    w = winter()
    summer_task = s.sched()
    winter_task = w.sched()
    # run forever
    while True:
        new_sched = get_schedule()
        if new_sched:
            winter_time = new_sched[0]
            summer_time = new_sched[0]
        # get the today date (tritron time must update to uptc time)
        today = datetime.datetime.now()
        # create datetime instance of winter and summer bracket
        winter_start = today.replace(
            month=winter_time['start']['month'], day=winter_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        winter_end = today.replace(
            month=winter_time['end']['month'], day=winter_time['start']['day'], hour=23, minute=59, second=59, microsecond=0)
        summer_start = today.replace(
            month=summer_time['start']['month'], day=summer_time['start']['day'], hour=0, minute=0, second=0, microsecond=0)
        summer_end = today.replace(
            month=summer_time['end']['month'], day=summer_time['start']['day'], hour=23, minute=59, second=59, microsecond=0)
        # check if today falls into summer
        if summer_start < today <= summer_end:
            # do nothing if schedule is already running. This to avoid reloading the schedule arasing saved schedule
            if not summer_running:
                summer_running = True  # set flag
                s = summer()  # reload the schedule
                summer_task = s.sched()
                summer_task.run_pending()
                winter_task.clear()
                winter_running = False
                print('Started summer sched')
            else:
                summer_task.run_pending()
        # check if today falls into winter
        elif winter_start <= today < winter_end:
            if not winter_running:
                winter_running = True
                w = winter()
                summer_task.clear()
                winter_task = w.sched()
                winter_task.run_pending()
                summer_running = False
                print('Started winter sched')
            else:
                winter_task.run_pending()
        else:
            pass
        sleep(1)


# running this script start the schedule
if __name__ == "__main__":
    # register the signals to be caught
    signal.signal(signal.SIGHUP, sig_handler)
    signal.signal(signal.SIGINT, terminateProcess)
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGILL, sig_handler)
    signal.signal(signal.SIGTRAP, sig_handler)
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGBUS, sig_handler)
    signal.signal(signal.SIGFPE, sig_handler)
    #signal.signal(signal.SIGKILL, sig_handler)
    signal.signal(signal.SIGUSR1, sig_handler)
    signal.signal(signal.SIGSEGV, sig_handler)
    signal.signal(signal.SIGUSR2, sig_handler)
    signal.signal(signal.SIGPIPE, sig_handler)
    signal.signal(signal.SIGALRM, sig_handler)
    signal.signal(signal.SIGTERM, terminateProcess)
    # run_schedule()
    try:
        modem_on(1)
        t = cold_test()
        s = t.sched()
        dog = dog_mode(mode=1)
        dog.run_all()
        mo = monitor()
        m = mo.sched()
        while True:
            m.run_pending()
            dog.run_pending()
            s.run_pending()
            with open('/media/mmcblk0p1/amigos/amigos/logs/sched.log', 'w+') as sched_log:
                sched_log.write(str(m.jobs)+',' + str(s.jobs))
            sleep(1)
    except Exception as err:
        printf('Scheduler failed with error message :' +
               str(err) + str(sys.exc_info()[0]) + '\n' + 'Trying to restart scheduler')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))
