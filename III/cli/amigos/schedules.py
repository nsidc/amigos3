# scheduling system
import schedule
import threading
import time
from copy import deepcopy


class print_sched(schedule.Scheduler):

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
