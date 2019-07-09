# from watchdog import set_mode
# from scheduler import run_schedule
from subprocess import Popen, PIPE
from execp import printf


def get_schedule():  # get the running schedule
    pass


def get_schedule_statut():  # is the schedule running ? what will run next.
    with open('/media/mmcblk0p1/amigos/amigos/logs/sched.log', 'r') as sched_log:
        data = sched_log.read()
    print(data)


def get_battery_voltage():  # get the voltage of the battery
    pass


def get_battery_current():  # get the voltage of the battery
    pass


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

    print(out2)


def schedule_health():
    out = None
    try:
        p = Popen("top -n 1 | grep python | grep -v grep",
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        out = p.communicate()
        out = out[0].split(' ')
        out = int(out[16])
    except:
        printf("Schedule health: Failed to check schedule health")
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
    get_schedule_statut()
