import watchdog as w
import os
from subprocess import Popen, PIPE, call
from onboard_device import get_battery_current, get_battery_voltage
import traceback
from gpio import all_off
import datetime
from time import sleep
from execp import printf
# Dictionary obeject to track schedule execution. index 0: task failure conter, Index 1:
# total task failure counter, index 2 Device name with description index 3:
# total successful run index 4: Number of run per hour
track = {"cr1000": [0, 0, "CR1000x", 0, 6],
         "readsolar": [0, 0, "Solar sensor", 0, 6],
         "vaisala": [0, 0, "Vaisala", 0, 6],
         "get_binex": [0, 0, "GPS Binex", 0, 1],
         "Out": [0, 0, "Dial_out", 0, 1],
         "send": [0, 0, "SBD out Tweet", 0, 1],
         "In": [0, 0, "Dial_in", 0, 1],
         "read_aquadopp": [0, 0, "Aquadopp", 0, 6],
         "read_seabird": [0, 0, "Sea Bird", 0, 6],
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


def first_time():
    if parm[1] is True:
        for item, array in track.items():
            track[item][3] = 0
            track[item][1] = 0
        parm[1] = False
    else:
        parm[0] = parm[0]+1
        for item, array in track.items():
            track[item][4] = track[item][4]*parm[0]
        return


def do_rerun(jobs, task):
    """Rerun a job that failed

    Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class (default: {None})
        task {string} -- Name of job/Device to rerun
    """
    for job in jobs:
        if job.job_func.__name__ == task:
            track[task][1] = 1 + \
                track[task][1]
            if track[task][0] > 1:
                track[task][0] = 0
                set_reschedule("")
                printf("Can not rerun {0} task that failed previously again. I must stay on schedule :)".format(
                    track[task][2]))
                return
            printf("Executing {0} task that failed previously. {1} total rerun :)".format(
                track[task][2], track[task][1]))
            next_second = job.next_run.second
            next_minute = job.next_run.minute
            next_hour = job.next_run.hour
            next_day = job.next_run.day
            next_month = job.next_run.month
            next_year = job.next_run.year
            printf("Schedule integrity will be altered :(")
            job.run()
            track[task][0] = track[task][0]+1
            job.next_run = job.next_run.replace(
                minute=next_minute, hour=next_hour, day=next_day, year=next_year, second=next_second, month=next_month)
            set_reschedule("")
            printf("Done rerunning {0} task. Schedule integrity was restored :)".format(
                track[task][2]))
            return


def get_rerun(jobs):
    """check for rerun

    Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class (default: {None}))
    """
    try:
        task = None
        with open("/media/mmcblk0p1/logs/reschedule.log", "r") as res:
            task = res.read()
        if task not in ["", None, " "]:
            do_rerun(jobs, task)

    except:
        printf("Rerun failed due to the following error, Might try again :)")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


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
    if re is not None:
        set_reschedule(re)
        re = None
    elif run is not None:
        track[run][3] = track[run][3]+1
        run = None
    elif start is True:
        first_time()
        start = False

    elif jobs:
        get_rerun(jobs)


def get_stat():
    """Print statistic to log file."""
    stat_dic = track
    printf('TF: Total failure', date=True)
    printf("TR: Total successfull run", date=True)
    printf("PE: Percent of execution", date=True)
    printf(" ________________ ____ ____ _____", date=True)
    printf("| Device         | TF | TR | PE  |", date=True)
    printf("|________________|____|____|_____|", date=True)
    printf("|________________|____|____|_____|", date=True)
    for array in stat_dic.values():
        ld = len(str(array[2]))
        ll = 14
        ldiff = ll-ld
        tota = array[4]
        printf("| " + str(array[2]) + " "*ldiff + " | " +
               str(array[1]) + " | " + str(array[3]) + " | " + str((array[3]/tota)*100) + " | ", date=True)
        printf("|________________|____|____|_____|", date=True)


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
        import shutil
        time_now = datetime.datetime.now()
        time_now = str(time_now.year) + "_" + str(time_now.month) + "_" + \
            str(time_now.day) + "_" + str(time_now.hour) + str(time_now.minute)
        if own:
            new_name = sub_files.split("/")
            new_name.insert(-1, "trashes")
            trash = "/".join(new_name[:-1])
            if os.path.isdir(trash) == False:
                os.mkdir(trash)
            new_name = "/".join(new_name)
            shutil.move(sub_files, new_name)
            return
        source = "/media/mmcblk0p1/backups/"
        folders = ["gps", "weather", "cr1000x", "solar", "dts", "pictures", "system"]
        time_now = datetime.datetime.now()
        time_now = str(time_now.year) + "_" + str(time_now.month) + "_" + \
            str(time_now.day) + "_" + str(time_now.hour) + "_" + str(time_now.minute)
        for index, item in enumerate(folders):
            if sub_files.find(item) != -1:
                new_name = source + item + "/" + \
                    time_now + "_" + sub_files.split("/")[-1]
        shutil.move(sub_files, new_name)
    except:
        printf("Files backup failed ")
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
        printf("Schedule health: Failed to check schedule health ``\\_(^/)_/``")


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
        printf(
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
            printf("Voltage reading biased: Reading {0} volt and {1} amps ``\\_(^/)_/``".format(
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
                printf('Voltage still too low, going back to a long sleep (1 hour). Reading {0} volt'.format(
                    voltage))
                call('rm /media/mmcblk0p1/logs/sleep.log', shell=True)
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(59), shell=True)
            else:
                with open('/media/mmcblk0p1/logs/sleep.log', 'w+') as sched_log:
                    sched_log.write('1')
                printf('Voltage too low, going back to 10 minutes sleep. Reading {0} volt'.format(
                    voltage))
                call(
                    "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(10), shell=True)
        elif voltage > 14.0:
            printf('Voltage is too high. Reading {0} volt ``\\_(^/)_/``'.format(
                voltage))
        else:
            printf('Voltage in normal operating range. Reading {0} volt :)'.format(
                voltage))
    except:
        printf('failed to excute put_to_sleep')
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
        printf("Schedule health: Failed to check schedule health ``\\_(^/)_/``")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    else:
        if out > 25000:
            printf(
                "Self destrying schedule ram memory consumption above {0} ``\\_(^/)_/``".format(out))
            kill()
        elif out < 17000:
            printf('Schedule health: Normal at {0} kb of ram'.format(out))
        elif out >= 17000 and out < 20000:
            printf('Schedule health: warning at {0} kb of ram'.format(out))
        elif out == None:
            printf('Schedule health: Scheduler not running ')

        else:
            printf(
                'Schedule health: critical  at {0} kb of ram. Scheduler would be terminated at over 25000 kb ``\\_(^/)_/``'.format(out))
