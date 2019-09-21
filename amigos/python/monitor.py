import datetime
import os
import traceback
from subprocess import PIPE, Popen, call
from time import sleep

import watchdog as w
from execp import printf
from gpio import all_off
from onboard_device import get_battery_current, get_battery_voltage

# Dictionary object to track schedule execution. index 0: task failure conter, Index 1:
# total task failure counter, index 2 Device name with description index 3:
# total successful run index 4: Number of run per hour
track = {
    "cr1000": [0, 0, "CR1000x", 0, 6, 0.576447027, 0, 0, 0, 0],
    "readsolar": [0, 0, "Solar sensor", 0, 6, 0.131056604, 0, 0, 0, 0],
    "vaisala": [0, 0, "Vaisala", 0, 6, 0.146047619, 0, 0, 0, 0],
    "get_binex": [0, 0, "GPS Binex", 0, 1, 0.281862069, 0, 0, 0, 0],
    "Out": [0, 0, "Dial_out", 0, 1, 0.941735425, 0, 0, 0, 0],
    "SBD": [0, 0, "SBD out Tweet", 0, 1, 0, 0.197106061, 0, 0, 0, 0],
    "In": [0, 0, "Dial_in", 0, 1, 0.554076212, 0, 0, 0, 0],
    "amigos_box_sort_AQ": [0, 0, "Aquadopp", 0, 3, 0, 0, 0, 0, 0],
    "amigos_box_sort_SB": [0, 0, "Sea Bird", 0, 6, 0, 0, 0, 0, 0],
    "ssh": [0, 0, "DTS", 0, 1, 0, 0, 0, 0, 0],
    "move": [0, 0, "Camera", 0, 1, 0, 0, 0, 0, 0],
    "get_stat_log": [0, 0, "Print Stat", 0, 1, 0, 0, 0, 0, 0],
}
parm = [0, True, 0.0, None]


def is_need_update(dts_time):
    """Check if time update is needed on the DTS

    Arguments:
        dts_time {str} -- time of the dts file last modified stored of the windows unit

    Returns:
        [Bool/Str] -- True if time has diverge since last file drop/ a time object
            of the newly datetime of files dropped on the window unit
    """
    printf("Checking if dts time has diverged")
    dts_time = dts_time.split("H")
    day = "-".join(dts_time[0:3])
    times = ":".join(dts_time[3:])
    dts_time = day + " " + times
    date_time_obj = datetime.datetime.strptime(dts_time, "%Y-%m-%d %H:%M:%S")
    # time_now = datetime.datetime.now()
    # diff = str(date_time_obj-time_now)
    return date_time_obj


def update_dts_time(jobs):
    """Update DTS time

    Arguments:
        jobs {LIST} -- List of all jobs

    Returns:
        Bool -- True if time has diverge false otherwise
    """
    try:
        from dts import get_dts_time

        printf("Reading last DTS files dropped time")
        dts_time = get_dts_time()
        update_time = is_need_update(dts_time)
        s_jobs = sorted(jobs)
        add = 4
        d_times = []
        for job in s_jobs:
            job_name = job.job_func.__name__
            if job_name == "ssh":
                job.next_run = (
                    update_time
                    - datetime.timedelta(minutes=7)
                    + datetime.timedelta(hours=add)
                )
                d_times.append(str(job.next_run.hour) + ":" + str(job.next_run.minute))
                add = add + 4
        with open("/media/mmcblk0p1/logs/dts_time", "w+") as d_time:
            dts_time = d_time.write("")
        printf("DTS Times are updated to {0}".format(d_times))
        return False
    except Exception:
        printf("Error updating dts schedule time")
        traceback.print_exc(file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def timing(device, dur):
    """Update durration of a job
    Arguments:
        device {[string]} -- task name
        dur {float} -- duration
    """
    for item, array in track.items():
        if item == device:
            track[item][6] = dur


def power_consumption():
    """Get the total power consumed

    Returns:
        [float] -- total power in Watt
    """
    consume = 0.0
    total_time = 0.0
    volt = get_battery_voltage()
    for item, array in track.items():
        consume = consume + (track[item][5] * volt * track[item][6]) * 0.000277778
        total_time = total_time + track[item][6]
        track[item][6] = 0
    parm[2] = parm[2] + consume
    return consume, total_time, parm[2]


def set_reschedule(device):
    """Set the reschedule.

    Arguments:
        device {string} -- The name of the sensor or device
    """
    with open("/media/mmcblk0p1/logs/reschedule.log", "w+") as res:
        res.write(device)


def first_time():
    """Check if the Dial out has run for the first time
    """
    if parm[1] is True:
        for item, array in track.items():
            track[item][3] = 0
            track[item][1] = 0
        parm[1] = False
    else:
        parm[0] = parm[0] + 1
        for item, array in track.items():
            track[item][4] = track[item][4] * parm[0]


def do_rerun(jobs, task):
    """Rerun a job that failed

    Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class
            (default: {None})
        task {string} -- Name of job/Device to rerun
    """
    for job in jobs:
        if job.job_func.__name__ == task:
            if track[task][0] > 1:
                track[task][0] = 0
                set_reschedule("")
                printf(
                    (
                        "Can not rerun {0} task that failed previously again. I must"
                        " stay on schedule :)"
                    ).format(track[task][2])
                )
                return
            printf(
                "Executing {0} task that failed previously. {1} total rerun :)".format(
                    track[task][2], track[task][1]
                )
            )
            next_second = job.next_run.second
            next_minute = job.next_run.minute
            next_hour = job.next_run.hour
            next_day = job.next_run.day
            next_month = job.next_run.month
            next_year = job.next_run.year
            printf("Schedule integrity will be altered :(")
            job.run()
            track[task][1] = 1 + track[task][1]
            track[task][0] = track[task][0] + 1
            job.next_run = job.next_run.replace(
                minute=next_minute,
                hour=next_hour,
                day=next_day,
                year=next_year,
                second=next_second,
                month=next_month,
            )
            set_reschedule("")
            printf(
                "Done rerunning {0} task. Schedule integrity was restored :)".format(
                    track[task][2]
                )
            )
            return


def reset_conter(jobs):
    """Reset the schedule time in the track dict

    Arguments:
        jobs {List} -- All Jobs(Schedules)
    """
    for job in jobs:
        job_name = job.job_func.__name__
        if job_name in track.keys():
            track[job_name][8] = 0
            track[job_name][7] = 0
            track[job_name][9] = 0


def get_restore_schedule(jobs):
    """Readjust the schedule if needed

    Arguments:
        jobs {List} -- All Jobs(Schedules)
    """
    delta_time = datetime.timedelta(hours=1)
    for job in jobs:
        last_run = job.last_run
        # print(last_run)
        next_run = job.next_run
        job_period = str(job.period)
        if job_period.find("day") == -1:
            if last_run:
                diff_run = next_run - last_run
                if diff_run > delta_time:
                    printf(
                        "(-) {0} schedule was distorted. Restoring ....".format(
                            track[job.job_func.__name__][2]
                        )
                    )
                    job.next_run = job.next_run - delta_time
                    printf(
                        "(-) {0} schedule back on track: {1}".format(
                            track[job.job_func.__name__][2],
                            str(job.next_run.hour) + ":" + str(job.next_run.minute),
                        )
                    )


def get_schedule(jobs):
    """Update the track dict to the lastest schedule runing

    Arguments:
        jobs {List} -- All Jobs(Schedules)
    """
    reset_conter(jobs)
    for job in jobs:
        job_name = job.job_func.__name__
        period = str(job.period)
        if job_name in track.keys():
            next_run = str(job.next_run.hour) + ":" + str(job.next_run.minute)
            if period.find("day") != -1:
                period = "Day"
                # track[job_name][1] = track[job_name][1]+1
            else:
                period = "Hour"
            track[job_name][9] = track[job_name][9] + 1
            track[job_name][7] = period
            track[job_name][8] = next_run


def get_rerun(jobs):
    """check for rerun

    Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class
            (default: {None}))
    """
    try:
        task = None
        with open("/media/mmcblk0p1/logs/reschedule.log", "r") as res:
            task = res.read()
        if task not in ["", None, " "]:
            do_rerun(jobs, task)
        get_schedule(jobs)
    except Exception:
        printf("Rerun failed due to the following error, Might try again :)")
        traceback.print_exc(file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def reschedule(jobs=None, start=False, re=None, run=None):
    """Rerun a task that has failed without affecting the integrity of the
    schedule.

    Keyword Arguments:
        jobs {Class } -- List of all jobs constructed from schedule as class
            (default: {None})
        stat {bool} -- To get the track dictionary (default: {False})
        re {string} -- Device or sensor name to reschedule (default: {None})
        run {string} -- Device or sensor name to updated successful run counter
            (default: {None})

    Returns:
        None/Dict -- Return none or Track as dictionary is stat set to True
    """
    if re is not None:
        set_reschedule(re)
        re = None
    if run is not None:
        track[run][3] = track[run][3] + 1
        run = None
    if start is True:
        first_time()
        start = False

    if jobs:
        get_rerun(jobs)


def get_stat_log():
    """Print stat table to  a log file
    """
    printf("Saving System Diagnostic table ")
    stat_dic = track
    power = power_consumption()[2]
    with open("/media/mmcblk0p1/logs/statictics", "a+") as stat:
        stat.write("Total Power consumed so far: {0} Watt\n".format(str(power)[0:-6]))
        stat.write("TF: Total failure\n")
        stat.write("TR: Total successfull run\n")
        stat.write("FR: Frequency of run\n")
        stat.write("TM: A time of run\n")
        stat.write("Qt: Total per FR\n")
        stat.write("PE: Percent of execution\n")
        stat.write(" ________________ ____ _____ ____ _____ _____ _____\n")
        stat.write("| Device         | FR | Qt | TM | TF  | TR  |  PE |\n")
        stat.write("|________________|____|_____|____|_____|_____|_____|\n")
        stat.write("|________________|____|_____|____|_____|_____|_____|\n")
    for array in stat_dic.values():
        ld = len(str(array[2]))
        ll = 14
        ldiff = ll - ld
        tota = array[4]
        percent = (array[3] * 100) / tota
        with open("/media/mmcblk0p1/logs/statictics", "a+") as stat:
            stat.write(
                "| "
                + str(array[2])
                + " " * ldiff
                + " | "
                + str(array[7])
                + " | "
                + str(array[9])
                + " | "
                + str(array[8])
                + " | "
                + str(array[1])
                + " | "
                + str(array[3])
                + " | "
                + str(percent)
                + " | \n"
            )
            stat.write("|________________|____|_____|____|_____|_____|_____|\n")
    with open("/media/mmcblk0p1/logs/statictics", "a+") as stat:
        stat.write("*" * 50 + "\n")
    printf("All done")


def get_stat():
    """Print statistic to log file."""
    stat_dic = track
    power = power_consumption()[2]
    printf("Total Power consumed so far: {0} Watt".format(str(power))[0:-6], date=True)
    printf("TF: Total failure", date=True)
    printf("TR: Total successfull run", date=True)
    printf("FR: Frequency of run", date=True)
    printf("TM: A time of run", date=True)
    printf("Qt: Total per FR ", date=True)
    printf("PE: Percent of execution", date=True)
    printf(" ________________ ____ _____ ____ _____ _____ _____", date=True)
    printf("| Device         | FR | Qt | TM | TF  | TR  |  PE |", date=True)
    printf("|________________|____|_____|____|_____|_____|_____|", date=True)
    printf("|________________|____|_____|____|_____|_____|_____|", date=True)
    for array in stat_dic.values():
        ld = len(str(array[2]))
        ll = 14
        ldiff = ll - ld
        tota = array[4]
        percent = (array[3] * 100) / tota
        printf(
            "| "
            + str(array[2])
            + " " * ldiff
            + " | "
            + str(array[7])
            + " | "
            + str(array[9])
            + " | "
            + str(array[8])
            + " | "
            + str(array[1])
            + " | "
            + str(array[3])
            + " | "
            + str(percent)
            + " | ",
            date=True,
        )
        printf("|________________|____|_____|____|_____|_____|_____|", date=True)


def get_disk_space():
    pass


def backup(sub_files, own=False, sbd=False):
    """Backup files.

    Arguments:
        sub_files {String} -- File + path
        sub_files {String} -- File + path

    Keyword Arguments:
        own {bool} -- Set if not auto generated by software (default: {False})
    """
    try:
        import shutil

        new_name = ""
        if own:
            new_name = sub_files.split("/")
            new_name.insert(-1, "trashes")
            trash = "/".join(new_name[:-1])
            if not os.path.isdir(trash):
                os.mkdir(trash)
            new_name = "/".join(new_name)
            shutil.move(sub_files, new_name)
            return
        source = "/media/mmcblk0p1/backups/"
        folders = [
            "gps",
            "weather",
            "cr1000x",
            "solar",
            "dts",
            "aquadopp",
            "picture",
            "seabird",
            "system",
        ]
        time_now = datetime.datetime.now()
        time_now = (
            str(time_now.year)
            + "_"
            + str(time_now.month)
            + "_"
            + str(time_now.day)
            + "_"
            + str(time_now.hour)
            + "_"
            + str(time_now.minute)
        )
        for index, item in enumerate(folders):
            if sub_files.find(item) != -1:
                if sub_files.find(".tar") == -1:
                    new_name = (
                        source + item + "/" + time_now + "_" + sub_files.split("/")[-1]
                    )
                else:
                    new_name = source + item + "/" + sub_files.split("/")[-1]

        shutil.move(sub_files, new_name)
        printf("Backed up {0}".format(sub_files.split("/")[-1]))

    except Exception:
        printf("Files backup failed ")
        traceback.print_exc(file=open("/media/mmcblk0p1/logs/system.log", "a+"))


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
        p = Popen(
            "top -n 1 | grep Mem | grep -v grep",
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        out = p.communicate()
        p = Popen(
            "top -n 1 | grep grep", stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True
        )
        out2 = p.communicate()
        out2 = out2[0].split("\n")
        out2 = out2[0].replace(" ", "")
        index = out2.find("rootS")
        grep = int(out2[(index + 5) : (index + 9)])  # noqa
        used_mem = int(out[0].split(" ")[1][:-1])
        free_mem = int(out[1].split(" ")[1][:-1])
        cached = int(out[4].split(" ")[1][:-1])
        buff = int(out[3].split(" ")[1][:-1])
        return used_mem - grep, free_mem + grep, cached, buff

    except Exception:
        return [0, 0, 0, 0]


def kill():
    """Find the pid of the scheduler process and Kill soft it."""
    out = None
    try:
        p = Popen(
            "top -n 1 | grep python | grep -v grep",
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        out = p.communicate()
        out = out[0].replace(" ", "")
        st = out.find("root")
        pid = int(out[0 : st - 1])  # noqa
        call("kill -2 {0}".format(pid), shell=True)
    except Exception:
        printf("Unable to find PID of the scheduler to Kill executiont\\_(*_*)_/``")


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
    next_job = sorted_jobs[0]
    next_job_name = track[next_job.job_func.__name__][2]
    next_run = sorted_jobs[0].next_run
    next_run_diff = next_run - datetime.datetime.now()
    time_interval = int(str(next_run_diff).split(":")[-2])
    str_time = str(next_run_diff)
    if time_interval < 3 or str_time.find("-") != -1:
        previous_job = parm[3]
        if previous_job != next_job:
            if time_interval > 3:
                time_interval = 60 - time_interval
                printf(
                    (
                        "~~~ Next task {0} job late by {1} minute(s)."
                        " Executing now ~~~"
                    ).format(next_job_name, time_interval)
                )
            else:
                printf(
                    "~~~ Next task {0} job in {1} minute(s). Waiting~~~".format(
                        next_job_name, time_interval
                    )
                )
            parm[3] = next_job
    elif no_task():
        keep_awake = None
        try:
            with open("/media/mmcblk0p1/logs/sleep_toggle", "r") as sle:
                keep_awake = sle.read()
        except Exception:
            pass
        if not keep_awake:
            power, totaltime, total = power_consumption()
            printf(
                "(*_*) Power consumed: {0} Wh. Total so far {1} Wh".format(
                    str(power)[0:-6], str(total)[0:-6]
                )
            )
            printf(
                " / \\ Next task: {0} job is in {1} minutes. Going on StandBy".format(
                    next_job_name, time_interval
                )
            )
            with open("/media/mmcblk0p1/logs/slept.log", "w+") as slept:
                slept.write("1")
            # with open("/media/mmcblk0p1/logs/schedule.log", ("a+")) as sch:
            #     sch.write(str(sorted(jobs)) + "\n" +
            #               str(time_interval) + "\n" + str_time+"#"*50 + "\n")
            w.toggle_1hour()
            # sleep(time_interval*60)
            all_off(1)
            sleep(2)
            call(
                "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(time_interval - 1),
                shell=True,
            )
    return next_job_name


def put_to_power_sleep():
    """Put Tritron to sleep if voltage level drop bellow treshold
    """
    voltage = get_battery_voltage()
    current = get_battery_current()
    try:
        if voltage < 2:
            voltage = voltage * 10
            printf(
                (
                    "Voltage reading biased: Reading {0} volt and {1} amps"
                    " ``\\_(*_*)_/``"
                ).format(voltage, current)
            )
        while voltage < 11.0:
            had_slept = None
            try:
                with open("/media/mmcblk0p1/logs/sleep.log", "r") as sched_log:
                    had_slept = sched_log.read()
            except Exception:
                pass
            keep_awake = None
            try:
                with open("/media/mmcblk0p1/logs/sleep_toggle", "r") as sle:
                    keep_awake = sle.read()
            except Exception:
                pass
            if not keep_awake:
                if had_slept:
                    printf(
                        (
                            "Voltage still too low, going back to a long sleep (1 hour)"
                            ". Reading {0} volt"
                        ).format(voltage)
                    )
                    all_off(1)
                    call("rm /media/mmcblk0p1/logs/sleep.log", shell=True)
                    call(
                        "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(59),
                        shell=True,
                    )
                else:
                    with open("/media/mmcblk0p1/logs/sleep.log", "w+") as sched_log:
                        sched_log.write("1")
                    printf(
                        (
                            "Voltage too low, going to 30 minutes sleep."
                            " Reading {0} volt"
                        ).format(voltage)
                    )
                    all_off(1)
                    call(
                        "bash /media/mmcblk0p1/amigos/bash/sleep {0}".format(30),
                        shell=True,
                    )
            voltage = get_battery_voltage()
        if voltage > 14.0:
            printf(
                "Voltage is too high. Reading {0} volt ``\\(_*_*)_/``".format(voltage)
            )
        else:
            printf(
                "Voltage in normal operating range. Reading {0} volt :)".format(voltage)
            )

    except Exception:
        w.printf("failed to excute put_to_sleep")
        traceback.print_exc(file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def get_schedule_health():
    """Get Ram memory consumption by the software
    """
    out = None
    try:
        p = Popen(
            "top -n 1 | grep python | grep -v grep",
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
        )
        out = p.communicate()
        out = out[0].replace(" ", "")
        st = out.find("root")
        out = int(out[st + 5 : st + 9])  # noqa
    except Exception:
        printf("Schedule health: Failed to check schedule health ``\\_(*_*)_/``")
        traceback.print_exc(file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    else:
        if out > 25000:
            printf(
                (
                    "Self destrying schedule ram memory consumption above {0}"
                    " ``\\_(*_*)_/``"
                ).format(out)
            )
            kill()
        elif out < 17000:
            printf("Schedule health: Normal at {0} kb of ram".format(out))
        elif out >= 17000 and out < 20000:
            printf("Schedule health: warning at {0} kb of ram".format(out))
        elif out is None:
            printf("Schedule health: Scheduler not running ")

        else:
            printf(
                (
                    "Schedule health: critical  at {0} kb of ram. "
                    "Scheduler would be terminated at over 25000 kb ``\\_(*_*)_/``"
                ).format(out)
            )
