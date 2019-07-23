# from watchdog import set_mode
# from scheduler import run_schedule
from subprocess import Popen, PIPE, call
from execp import printf
from onboard_device import get_battery_current, get_battery_voltage
import traceback
from gpio import all_off
import datetime


def get_schedule():  # get the running schedule
    pass


def get_disk_space():
    pass


def backup():
    pass


def free_space():
    pass


def has_slept():
    data = None
    with open("/media/mmcblk0p1/logs/slept.log", "r") as slept:
        data = slept.read()
    if data:
        return True
    return False


def clear_cached():
    """
    clear the cache memory
    """
    call("sync; echo 1 > /proc/sys/vm/drop_caches", shell=True)


def get_system_performance():  # get how much cpu, memory is been used
    """
    Return the ram usage, cached and  buffer memory
    """
    p = Popen("top -n 1 | grep Mem | grep -v grep",
              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out = p.communicate()
    out = out[0].split(':')[1].split(',')
    # print(out)
    p = Popen("top -n 1 | grep grep",
              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out2 = p.communicate()
    out2 = out2[0].split('\n')
    out2 = out2[0].replace(' ', '')
    index = out2.find('rootS')
    grep = int(out2[index+5:index+9])
    used_mem = int(out[0].split(" ")[1][:-1])
    free_mem = int(out[1].split(" ")[1][:-1])
    cached = int(out[4].split(" ")[1][:-1])
    buff = int(out[3].split(" ")[1][:-1])
    return used_mem-grep, free_mem+grep, cached, buff
    # for process in out2:
    #     mem = process.split(' ')


def kill():
    """
    Find the pid of the scheduler process and Kill the scheduler
    """
    out = None
    try:
        p = Popen("top -n 1 | grep python | grep -v grep",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out = p.communicate()
        out = out[0].replace(' ', '')
        st = out.find('root')
        pid = int(out[0:st-1])
        call("kill -2 {0}".format(pid), shell=True)
    except:
        printf("Schedule health: Failed to check schedule health")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def no_task():
    """
    Check if the amigos is busy executing a task
    """
    data = None
    with open("/media/mmcblk0p1/logs/power_log.log", "r") as power:
        data = power.read()
    data = data.split(",")
    print(data)
    if int(data[0], 2) == 0 and int(data[2], 2) == 0:
        if int(data[1], 2) == 8 or int(data[1], 2) == 0:
            return True
    return False


def put_to_inactive_sleep():
    """
    Send the system to sleep if no task is schedule in the nest 3 minute
    """
    data = None
    with open("/media/mmcblk0p1/logs/schedule.log", "r") as schedule:
        data = schedule.read()
    data = data.split(",")[1]
    next_run = None
    now = datetime.datetime.now()
    if data:
        next_run = data.split(" ")
        # print(next_run)
        years, months, days = next_run[3].split("-")
        hours, minutes, seconds = next_run[4][0:-1].split(":")
        next_run = now.replace(year=int(years),
                               month=int(months), day=int(days), hour=int(hours), minute=int(minutes), second=int(seconds))
    time_interval = int(str(next_run-now).split(":")[1])-2
    # print(interval)

    if time_interval < 3:
        pass
    elif no_task():
        # if interval> 52:
        printf(
            "No task in the next {0} minutes. Going on StandBy".format(time_interval))
        with open("/media/mmcblk0p1/logs/slept.log", "w+") as slept:
            slept.write("1")
        all_off(1)
        call(
            "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(time_interval), shell=True)


def put_to_power_sleep():
    voltage = get_battery_voltage()
    current = get_battery_current()
    try:
        if voltage < 2:
            voltage = voltage*10
            printf("Voltage reading biased: Reading {0} volt and {1} amps".format(
                voltage, current))
        if voltage < 11.0:
            had_slept = None
            try:
                with open('/media/mmcblk0p1/logs/sleep.log', 'r') as sched_log:
                    had_slept = sched_log.read()
            except:
                pass
            if had_slept:
                all_off(1)
                printf('Voltage still too low, going back to a long sleep (1 hour). Reading {0} volt and {1} amps'.format(
                    voltage, current))
                call('rm /media/mmcblk0p1/logs/sleep.log', shell=True)
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(59), shell=True)
            else:
                with open('/media/mmcblk0p1/logs/sleep.log', 'w+') as sched_log:
                    sched_log.write('1')
                printf('Voltage too low, going back to 3 minutes sleep. Reading {0} volt and {1} amps'.format(
                    voltage, current))
                # call(
                # "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(10), shell = True)
        elif voltage > 14.0:
            printf('Voltage is too high. Reading {0} volt and {1} amps'.format(
                voltage, current))
        else:
            printf('Voltage in normal operating range. Reading {0} volt and {1} amps'.format(
                voltage, current))
    except:
        printf('failed to excute put_to_sleep')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def get_schedule_health():
    out = None
    try:
        p = Popen("top -n 1 | grep python | grep -v grep",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out = p.communicate()
        out = out[0].replace(' ', '')
        st = out.find('root')
        out = int(out[st+5:st+10])
    except:
        printf("Schedule health: Failed to check schedule health")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    else:
        if out > 20000:
            printf(
                "Self destrying schedule ram memory consumption above {0}".format(out))
            kill()
        elif out < 15000:
            printf('Schedule health: Normal at {0} kb of ram'.format(out))
        elif out >= 15000 and out < 17000:
            printf('Schedule health: warning at {0} kb of ram'.format(out))
        elif out == None:
            printf('Schedule health: Scheduler not running')

        else:
            printf(
                'Schedule health: critical  at {0} kb of ram. Scheduler would be terminated at over 20000 kb'.format(out))


if __name__ == "__main__":
    get_system_performance()
