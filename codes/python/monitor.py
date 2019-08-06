import watchdog as w
import os
from subprocess import Popen, PIPE, call
from onboard_device import get_battery_current, get_battery_voltage
import traceback
from gpio import all_off
import datetime
from time import sleep
import shutil


def get_schedule():  # get the running schedule
    pass


def get_disk_space():
    pass


def backup(sub_files, own=False):
    try:
        # files = ["gps_binex.log", "weather_data.log", "thermostat.log", "solar.log", ]
        time_now = datetime.datetime.now()
        time_now = str(time_now.year) + "_" + str(time_now.month) + "_" + \
            str(time_now.day) + "_" + str(time_now.hour) + str(time_now.minute)
        if own:
            new_name = sub_files.split("/")
            new_name.insert(-1, "trashes")
            # print(new_name[:-1])
            trash = "/".join(new_name[:-1])
            if os.path.isdir(trash) == False:
                print(os.path.isdir("-".join(new_name[:-1])))
                print(trash)
                os.mkdir(trash)
            # print(new_name)
            new_name = "/".join(new_name)
            shutil.move(sub_files, new_name)
            return
        # source = "/media/mmcblk0p1/logs"
        gps = "/media/mmcblk0p1/backups/gps"
        cr1000 = "/media/mmcblk0p1/backups/cr1000x"
        weather = "/media/mmcblk0p1/backups/weather"
        dts = "/media/mmcblk0p1/backups/dts"
        solar = "/media/mmcblk0p1/backups/solar"
        photo = "/media/mmcblk0p1/backups/pictures"
        system = "/media/mmcblk0p1/backups/system"
        time_now = datetime.datetime.now()
        time_now = str(time_now.year) + "_" + str(time_now.month) + "_" + \
            str(time_now.day) + "_" + str(time_now.hour) + str(time_now.minute)
        # for sub_files in files:
        if sub_files.find("gps") != -1:
            new_name = gps + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("weather") != -1:
            new_name = weather + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("therm") != -1:
            new_name = cr1000 + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("solar") != -1:
            new_name = solar + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("dts") != -1:
            new_name = dts + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("picture") != -1:
            new_name = photo + "/" + time_now + sub_files.split("/")[-1]
        elif sub_files.find("system") != -1:
            new_name = system + "/" + time_now + sub_files.split("/")[-1]
        # print(sub_files, new_name)
        shutil.move(sub_files, new_name)
    except:
        w.printf("Files backup failed ")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def free_space():
    pass


def has_slept():
    data = None
    with open("/media/mmcblk0p1/logs/slept.log", "r") as slept:
        data = slept.read()
    if data:
        with open("/media/mmcblk0p1/logs/slept.log", "w") as slept:
            data = slept.write("")
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
        w.printf("Schedule health: Failed to check schedule health ``\\_(^/)_/``")
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
    if int(data[0], 2) == 0 and int(data[2], 2) == 0:
        if int(data[1], 2) == 8 or int(data[1], 2) == 0:
            return True
    return False


def put_to_inactive_sleep(jobs):
    """
    Send the system to sleep if no task is scheduled in the nest 3 minute
    """
    # data = None
    # with open("/media/mmcblk0p1/logs/schedule.log", "r") as schedule:
    #     data = schedule.read()
    # data = data.split(",")[1]
    # next_run = None

    time_interval = int(
        str(sorted(jobs)[0].next_run - datetime.datetime.now()).split(":")[1])
    str_time = str(sorted(jobs)[0].next_run - datetime.datetime.now()).split(":")
    # if data:
    #     next_run = data.split(" ")
    #     # print(next_run)
    #     years, months, days = next_run[3].split("-")
    #     hours, minutes, seconds = next_run[4][0:-1].split(":")
    #     next_run = now.replace(year=int(years),
    #                            month=int(months), day=int(days), hour=int(hours), minute=int(minutes), second=int(seconds))
    # time_interval = int(str(next_run-now).split(":")[1])-2
    # print(interval)
    # print(time_interval, str_time)
    if time_interval < 3 or str_time[0].find("-") != -1:
        pass
    elif no_task():
        # if interval> 52:
        w.printf(
            "No task in the next {0} minutes. Going on StandBy".format(time_interval))
        with open("/media/mmcblk0p1/logs/slept.log", "w+") as slept:
            slept.write("1")
        w.toggle_1hour()
        sleep(time_interval*60)

        # all_off(1)
        # call(
        #     "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(time_interval), shell=True)


def put_to_power_sleep():
    voltage = get_battery_voltage()
    current = get_battery_current()
    try:
        if voltage < 2:
            voltage = voltage*10
            w.printf("Voltage reading biased: Reading {0} volt and {1} amps ``\\_(^/)_/``".format(
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
                w.printf('Voltage still too low, going back to a long sleep (1 hour). Reading {0} volt and {1} amps'.format(
                    voltage, current))
                call('rm /media/mmcblk0p1/logs/sleep.log', shell=True)
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(59), shell=True)
            else:
                with open('/media/mmcblk0p1/logs/sleep.log', 'w+') as sched_log:
                    sched_log.write('1')
                w.printf('Voltage too low, going back to 10 minutes sleep. Reading {0} volt and {1} amps'.format(
                    voltage, current))
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(10), shell=True)
        elif voltage > 14.0:
            w.printf('Voltage is too high. Reading {0} volt and {1} amps ``\\_(^/)_/``'.format(
                voltage, current))
        else:
            w.printf('Voltage in normal operating range. Reading {0} volt and {1} amps :)'.format(
                voltage, current))
    except:
        w.printf('failed to excute put_to_sleep')
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
        w.printf("Schedule health: Failed to check schedule health ``\\_(^/)_/``")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    else:
        if out > 20000:
            w.printf(
                "Self destrying schedule ram memory consumption above {0} ``\\_(^/)_/``".format(out))
            kill()
        elif out < 15000:
            w.printf('Schedule health: Normal at {0} kb of ram'.format(out))
        elif out >= 15000 and out < 17000:
            w.printf('Schedule health: warning at {0} kb of ram'.format(out))
        elif out == None:
            w.printf('Schedule health: Scheduler not running ')

        else:
            w.printf(
                'Schedule health: critical  at {0} kb of ram. Scheduler would be terminated at over 20000 kb ``\\_(^/)_/``'.format(out))


# if __name__ == "__main__":
#     w.printf("\n" + " "*10 + "*****   *****   *****" + " "*10 + "\n" + " "*10 + "Hi there, I am the Amigos {0} version III." + " "*10 + "\n" +
#              "Here, you will find all my actions since I was powered on." + " "*10+"\n" + " "*10 + "*****   *****   *****" + " "*10 + "\n".format(amigos_Unit()), date=True)
