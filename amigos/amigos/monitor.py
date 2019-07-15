# from watchdog import set_mode
# from scheduler import run_schedule
from subprocess import Popen, PIPE, call
from execp import printf
from time import sleep
from onboard_device import get_battery_current, get_battery_voltage
from watchdog import set_mode
import traceback


def get_schedule():  # get the running schedule
    pass


def get_schedule_statut():  # is the schedule running ? what will run next.
    with open('/media/mmcblk0p1/amigos/amigos/logs/sched.log', 'r') as sched_log:
        data = sched_log.read()
    # print(data)


def get_system_performance():  # get how much cpu, memory is been used
    p = Popen("top -n 1 | grep Mem | grep -v grep",
              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out = p.communicate()
    out = out[0].split(':')[1].split(',')
    p = Popen("top -n 1 | grep grep",
              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    out2 = p.communicate()
    out2 = out2[0].split('\n')
    for process in out2:
        mem = process.split(' ')


def put_to_sleep():
    voltage = get_battery_voltage()
    current = get_battery_current()
    try:
        if voltage < 2:
            voltage = voltage*10
            printf("Voltage reading biased, it is getting too cold here: Reading {0} volt and {1} amps".format(
                voltage, current))
        if voltage < 11.0:
            had_slept = None
            try:
                with open('/media/mmcblk0p1/amigos/amigos/logs/sleep.log', 'r') as sched_log:
                    had_slept = sched_log.read()
            except:
                pass
            if had_slept:
                printf('Voltage still too low, going on long sleep (1 hour). Reading {0} volt and {1} amps'.format(
                    voltage, current))
                call('rm /media/mmcblk0p1/amigos/amigos/logs/sleep.log', shell=True)
                # set_mode(2)
            else:
                with open('/media/mmcblk0p1/amigos/amigos/logs/sleep.log', 'w+') as sched_log:
                    sched_log.write('1')
                printf('Voltage too low, going on 3 minutes sleep. Reading {0} volt and {1} amps'.format(
                    voltage, current))
                # set_mode(3)
        elif voltage > 14.0:
            printf('Voltage is to high. Reading {0} volt and {1} amps'.format(
                voltage, current))
        else:
            printf('Voltage in normal operating range. Reading {0} volt and {1} amps'.format(
                voltage, current))
    except:
        printf('failed to excute put_to_sleep')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))


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
            file=open("/media/mmcblk0p1/amigos/amigos/logs/system.log", "a+"))
    else:
        if out < 15000:
            printf('Schedule health: Normal at {0} Mb of ram'.format(out))
        elif out >= 15000 and out < 17000:
            printf('Schedule health: warning at {0} Mb of ram'.format(out))
        elif out == None:
            printf('Schedule health: Scheduler not running')
        else:
            printf('Schedule health: critical  at {0} Mb of ram'.format(out))


if __name__ == "__main__":
    get_schedule_health()
