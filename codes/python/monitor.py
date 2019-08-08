import watchdog as w
import os
from subprocess import Popen, PIPE, call
from onboard_device import get_battery_current, get_battery_voltage
import traceback
from gpio import all_off
import datetime
from time import sleep
import shutil

# Dictionary obeject to track schedule execution. index 0: task failure conter, Index 1: total task failure counter, index 2 Device name with description index 3: total successful run index 4: Number of run per hour
track = {"cr1000": [0, 0, "CR1000x", 0, 6],
         "readsolar": [0, 0, "Solar sensor", 0, 6],
         "vaisala": [0, 0, "Vaisala", 0, 6],
         "get_binex": [0, 0, "GPS Binex", 0, 1],
         "Out": [0, 0, "Dial_out", 0, 1],
         "send": [0, 0, "SBD out Tweet", 0, 1],
         "In": [0, 0, "Dial_in", 0, 1],
         "read_aquadopp": [0, 0, "Aquadopp", 0, 1],
         "read_seabird": [0, 0, "Sea Bird", 0, 1],
         "test": [0, 0, "DTS", 0, 1],
         "move": [0, 0, "Camera", 0, 1],
         }
parm = [0, True]


def set_reschedule(device):
    """Set the reschedule.

    Arguments:
        device {string} -- The name of the sensor or device
    """
    with open("/media/mmcblk0p1/logs/reschedule.log", "w+") as res:
        res.write(device)


def reschedule(jobs=None, start=False, re=None, run=None):
    """Rerun a task that has failed without affecting the integrity of the
    schedule.

    Keyword Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class (default: {None})
        stat {bool} -- To get the track dictionary (default: {False})
        re {string} -- Device or sensor name to reschedule (default: {None})
        run {string} -- Device or sensor name to updated successful run counter (default: {None})

    Returns:
        None/Dict -- Return none or Track as dictionary is stat set to True
    """
    if re != None:
        with open("/media/mmcblk0p1/logs/reschedule.log", "w+") as res:
            res.write(re)
        re = None
        return
    elif run != None:
        track[run][3] = track[run][3]+1
        run = None
        return
    elif start == True:
        if parm[1] == True:
            for item, array in track.items():
                track[item][3] = 0
            parm[1] = False
            return
        parm[0] = parm[0]+1
        for item, array in track.items():
            track[item][4] = array[4]*parm[0]
        start = False
        return

    elif jobs:
        try:
            task = None
            with open("/media/mmcblk0p1/logs/reschedule.log", "r") as res:
                task = res.read()
            if task in ["", None, " "]:
                pass
            else:
                for job in jobs:
                    total_run = track[job.job_func.__name__][1]+1
                    track[job.job_func.__name__][1] = total_run + \
                        track[job.job_func.__name__][1]
                    if track[job.job_func.__name__][0] > 1:
                        track[job.job_func.__name__][0] = 0
                        set_reschedule("")
                        w.printf("Can not rerun {0} task that failed previously again. I must stay on schedule :)".format(
                            track[job.job_func.__name__][2]))
                        return
                    elif job.job_func.__name__ == task:
                        w.printf("Executing {0} task that failed previously. {1} total rerun :)".format(
                            track[job.job_func.__name__][2], track[job.job_func.__name__][1]))
                        next_second = job.next_run.second
                        next_minute = job.next_run.minute
                        next_hour = job.next_run.hour
                        next_day = job.next_run.day
                        next_month = job.next_run.month
                        next_year = job.next_run.year
                        w.printf("Schedule integrity will be altered :(")
                        job.run()
                        track[job.job_func.__name__][0] = track[job.job_func.__name__][0]+1
                        job.next_run = job.next_run.replace(
                            minute=next_minute, hour=next_hour, day=next_day, year=next_year, second=next_second, month=next_month)
                        set_reschedule("")
                        w.printf("Done rerunning {0} task. Schedule integrity was restored :)".format(
                            track[job.job_func.__name__][2]))
        except:
            w.printf("Rerun failed due to the following error, Might try again :)")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def get_stat():
    """Print statistic to log file."""
    stat_dic = track
    ll = 14
    w.printf('TF: Total failure', date=True)
    w.printf("TR: Total successfull run", date=True)
    w.printf("PE: Percent of execution", date=True)
    w.printf(" ________________ ____ ____ _____", date=True)
    w.printf("| Device         | TF | TR | PE  |", date=True)
    w.printf("|________________|____|____|_____|", date=True)
    w.printf("|________________|____|____|_____|", date=True)
    for array in stat_dic.values():
        ld = len(str(array[2]))
        ldiff = ll-ld
        tota = array[4]
        w.printf("| " + str(array[2]) + " "*ldiff + " | " +
                 str(array[1]) + " | " + str(array[3]) + " | " + str((array[3]/tota)*100) + " | ", date=True)
        w.printf("|________________|____|____|_____|", date=True)


def get_schedule():  # get the running schedule
    pass


def get_disk_space():
    pass


def backup(sub_files, own=False):
    """Backup files.

    Arguments:
        sub_files {String} -- File + path
        sub_files {String} -- File + path

    Keyword Arguments:
        own {bool} -- Set if not auto generated by software (default: {False})
    """
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
            w.printf("Dial out session complete! File tree is cleaned :)")
        # print(sub_files, new_name)
        shutil.move(sub_files, new_name)
    except:
        w.printf("Files backup failed ")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def free_space():
    pass


def has_slept():
    """Has the Tritron went to sleep?

    Returns:
        Bool -- True if Tritron was at sleep  False otherwise
    """
    data = None
    with open("/media/mmcblk0p1/logs/slept.log", "r") as slept:
        data = slept.read()
    if data:
        with open("/media/mmcblk0p1/logs/slept.log", "w") as slept:
            data = slept.write("")
        return True
    return False


def clear_cached():
    """clear the cache memory."""
    call("sync; echo 1 > /proc/sys/vm/drop_caches", shell=True)


def get_system_performance():  # get how much cpu, memory is been used
    """cached and  buffer memory.

    Return:
        String: Return the ram usage, cached and  buffer memory
    """
    try:
        p = Popen("top -n 1 | grep Mem | grep -v grep",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out = p.communicate()
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
    except:
        return[0, 0, 0, 0]


def kill():
    """Find the pid of the scheduler process and Kill soft it."""
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
    """Send the system to sleep if no task is scheduled in the nest 3
    minute."""

    sorted_jobs = sorted(jobs)
    next_run = sorted_jobs[0].next_run
    next_run_diff = next_run - datetime.datetime.now()
    time_interval = int(str(next_run_diff).split(":")[-2])
    str_time = str(next_run_diff)
    if time_interval < 3 or str_time.find("-") != -1:
        sleep(1)
    elif no_task():
        # if interval> 52:
        w.printf(
            "Next task: {0} job is in {1} minutes. Going on StandBy".format(track[sorted_jobs[0].job_func.__name__][2], time_interval))
        with open("/media/mmcblk0p1/logs/slept.log", "w+") as slept:
            slept.write("1")
        w.toggle_1hour()
        sleep(time_interval*60)

        # all_off(1)
        # call(
        #     "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(time_interval), shell=True)


def put_to_power_sleep():
    """Put Tritron to sleep if voltage level drop bellow treshold
    """
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
                w.printf('Voltage still too low, going back to a long sleep (1 hour). Reading {0} volt'.format(
                    voltage))
                call('rm /media/mmcblk0p1/logs/sleep.log', shell=True)
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(59), shell=True)
            else:
                with open('/media/mmcblk0p1/logs/sleep.log', 'w+') as sched_log:
                    sched_log.write('1')
                w.printf('Voltage too low, going back to 10 minutes sleep. Reading {0} volt'.format(
                    voltage))
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(10), shell=True)
        elif voltage > 14.0:
            w.printf('Voltage is too high. Reading {0} volt ``\\_(^/)_/``'.format(
                voltage))
        else:
            w.printf('Voltage in normal operating range. Reading {0} volt :)'.format(
                voltage))
    except:
        w.printf('failed to excute put_to_sleep')
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def get_schedule_health():
    """Get Ram memory consumption by the software
    """
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
        if out > 25000:
            w.printf(
                "Self destrying schedule ram memory consumption above {0} ``\\_(^/)_/``".format(out))
            kill()
        elif out < 17000:
            w.printf('Schedule health: Normal at {0} kb of ram'.format(out))
        elif out >= 17000 and out < 20000:
            w.printf('Schedule health: warning at {0} kb of ram'.format(out))
        elif out == None:
            w.printf('Schedule health: Scheduler not running ')

        else:
            w.printf(
                'Schedule health: critical  at {0} kb of ram. Scheduler would be terminated at over 25000 kb ``\\_(^/)_/``'.format(out))


# if __name__ == "__main__":
#     w.printf("\n" + " "*10 + "*****   *****   *****" + " "*10 + "\n" + " "*10 + "Hi there, I am the Amigos {0} version III." + " "*10 + "\n" +
#              "Here, you will find all my actions since I was powered on." + " "*10+"\n" + " "*10 + "*****   *****   *****" + " "*10 + "\n".format(amigos_Unit()), date=True)
