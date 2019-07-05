# from watchdog import set_mode
# from scheduler import run_schedule
from subprocess import Popen, PIPE


def get_schedule():  # get the running schedule
    pass


def get_schedule_statut():  # is the schedule running ? what will run next.
    pass


def get_battery_voltage():  # get the voltage of the battery
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
        mem=process.split(' ')

    print(out2)


if __name__ == "__main__":
    get_system_performance()
