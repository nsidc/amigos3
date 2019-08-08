# Battery, CPU and other ressources monitoring
from time import sleep
import subprocess
from execp import printf


def toggle_1hour():
    """
    set the watchdog to 1hour
    """
    subprocess.call('echo 3 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 0 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 3 > /sys/class/gpio/wdt_ctl/data', shell=True)


def __toggle_3min():
    """
    set the watchdog to 3min
    """
    # set the power mode
    subprocess.call('echo 1 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 0 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 1 > /sys/class/gpio/wdt_ctl/data', shell=True)


#     wdog = schedule.Scheduler()
#     if mode is 0 or mode is None:  # reset the power to the boar every hour. This keep the board on continuously
#         wdog.every(45).minutes.do(__toggle_1hour).tag('hourly-dog')
#     elif mode == 1:  # reset the power to the boar every 2.5 minutes. This keep the board on continuously
#         wdog.every(1).minutes.do(__toggle_3min).tag('3min-dog')
#         printf("Auto watchdog is set to 3 minutes")
#         return wdog
#     elif mode == 3:
#         subprocess.call(
#             "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(Sleep_time), shell=True)
#         return
#     return wdog


# def run_dog(mode=None):
#     wdog = set_mode(mode)

#     wdog.run_all()
#     while True:
#         wdog.run_pending()
#         sleep(1)
#     # run a thread in background
#     # run_task()
#     # while True:
#     #     printf(st1.isDaemon())
#     #     printf(schedule.next_run())
#     # sleep(1)
