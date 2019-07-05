# Battery, CPU and other ressources monitoring
from time import sleep
from schedule import schedule
import subprocess


def __toggle_1hour():
    # set the power mode
    subprocess.call('echo 3 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 0 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 3 > /sys/class/gpio/wdt_ctl/data', shell=True)
    print("Auto watchdog is set to  1 hour")


def __toggle_3min():
    # set the power mode
    subprocess.call('echo 1 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 0 > /sys/class/gpio/wdt_ctl/data', shell=True)
    sleep(2)
    subprocess.call('echo 1 > /sys/class/gpio/wdt_ctl/data', shell=True)
    print("Auto watchdog is set to  3 min")


def __go_sleep_3min():
    # put the board to sleep for 3 min
    subprocess.call('bash /media/mmcblk0p1/sleep_3min', shell=True)


def __go_sleep_1hour():
    # put the board to sleep for 3 min
    subprocess.call('bash /media/mmcblk0p1/sleep_1hour', shell=True)


def set_mode(mode=None):
    wdog = schedule.Scheduler()
    if mode is 0 or mode is None:  # reset the power to the boar every hour. This keep the board on continuously
        wdog.every(45).minutes.do(__toggle_1hour).tag('hourly-dog')
    elif mode == 1:  # reset the power to the boar every 2.5 minutes. This keep the board on continuously
        wdog.clear('hourly-dog')
        wdog.every(1).minutes.do(__toggle_3min.tag('3min-dog'))
        print("Auto watchdog is set to 3 minutes")
        return
    elif mode == 3:
        __go_sleep_3min()
        return
    elif mode == 2:
        __go_sleep_1hour()
        return
    return wdog


def run_dog(mode=None):
    wdog = set_mode(mode)
    wdog.run_all()
    while True:
        wdog.run_pending()
        sleep(1)
    # run a thread in background
    # run_task()
    # while True:
    #     print(st1.isDaemon())
    #     print(schedule.next_run())
    # sleep(1)
