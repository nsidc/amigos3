# # scheduling system
from schedule import schedule as schedule
from time import sleep
from datetime import datetime
from gps import gps_data as gps_data
from gpio import power_up
from vaisala import average_data as average_data
from onvif.onvif import ptz_client as ptz
from cr1000x import cr1000x as cr1000x
from onboard_device import get_humidity, get_temperature
from solar import readsolar
# import monitor as monitor


class cold_test():
    def __init__(self, *args, **kwargs):
        self.sched_test = schedule.Scheduler()  # create a new schedule instance

    def vaisala_schedule(self):
        # Perform this measurement reading every hour between :58 to :00
        self.sched_test.every().hour.at(":10").do(average_data)  # add vaisala schedule

        self.sched_test.every().hour.at(":50").do(average_data)  # add vaisala schedule

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_test.every().hour.at(":30").do(gps.get_binex)

    def camera_schedule(self):
        cam = ptz()
        self.sched_test.every().hour.at(":45").do(cam.cam_test)
        self.sched_test.every().hour.at(":01").do(cam.cam_test)

    def cr100x_schedule(self):
        # add cr100 schedules
        cr = cr1000x()
        self.sched_test.every().hour.at(":20").do(cr.write_file)
        self.sched_test.every().hour.at(":05").do(cr.write_file)

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
        # Perform this measurement reading every hour between :58 to :00
        self.sched_summer.every().hour.at(":58").do(average_data)  # add vaisala schedule

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
        self.sched_summer.every().hour.at(":55").do(write_file)

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
        # Perform this measurement reading every hour between :58 to :00
        self.sched_winter.every().hour.at(":58").do(average_data)

    def gps_schedule(self):
        gps = gps_data()
        # add gps schedules
        self.sched_winter.every().day.at("23:10").do(gps.get_binex)

    def camera_schedule(self):
        pass

    def cr100x_schedule(self):
        # add cr100x schedules
        self.sched_winter.every().hour.at(":55").do(write_file)

    def sched(self):
        # load all the winter schedule
        self.vaisala_schedule()
        self.camera_schedule()
        self.gps_schedule()
        self.cr100x_schedule()
        return self.sched_winter


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
    # run_schedule()
    power_up(1)
    t = cold_test()
    s = t.sched()
    while True:
        s.run_pending()
        sleep(1)
