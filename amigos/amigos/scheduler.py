# scheduling system
from schedule import schedule as schedule
import threading
import time
from copy import deepcopy
import monitor as monitor


class power_control(schedule.Scheduler):
    def __init__(self):
        pass

    def watchdog(self, arg=1):
        wdog = schedule.Scheduler()
        if arg == 1:
            try:
                wdog.clear('three-minutes-dog')
            except:
                pass
            wdog.every(1).hour.do(monitor.watchdog, value=1).tag('hourly-dog')
            print "Auto watchdog is set to  1 hour"
        elif arg == 'deactivate':
            try:
                wdog.clear('three-minutes-dog')
            except:
                pass
            try:
                wdog.clear('hourly-dog')
            except:
                pass
            print "Auto watchdog is set to off"

        else:
            wdog.clear('hourly-dog')
            wdog.every(3).minutes.do(monitor.watchdog,
                                     value=3).tag('three-minutes-dog')
            print "Auto watchdog is set to 3 minutes"

    def power(self, value):
        pass


class weather_recor(schedule.Scheduler):

    def job(self):
        pass

    def task(self, running=False):
        sh = schedule.Scheduler()
        sh.every(10).seconds.do(self.job)
        sh.every().hour.do(self.job)
        sh.every().day.at("10:30").do(self.job)
        sh.every(5).to(10).minutes.do(self.job)
        sh.every().wednesday.at("13:15").do(self.job)
        sh.every().minute.at(":17").do(self.job)
        while 1:
            sh.run_pending()
            time.sleep(3)
            if sh.all_jobs():
                with open('text.txt', 'w') as file:
                    jobs = sh.all_jobs()
                    for job in jobs:
                        file.write(str(job) + "\n")

    def start_task(self):
        st1 = threading.Thread(target=self.task)
        st1.start()
        return st1

    def print_all(self):
        print(threading.active_count())
        print(schedule.next_run())
        self.task()
