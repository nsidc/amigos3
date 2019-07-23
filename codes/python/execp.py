import functools
import datetime
from schedule import schedule as schedule
import sys


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


def printf(message):
    with open('/media/mmcblk0p1/amigos/amigos/logs/system.log', 'a+') as log:
        date = str(datetime.datetime.now()) + ': '
        log.write(date + message + '\n')


def sig_handler(signum, frame):
    # save the state here or do whatever you want
    printf('Scheduler has received signal {0}'.format(str(signum)))


def terminateProcess(signalNumber, frame):
    printf('received (SIGTERM),  terminating the scheduler. System must be going down or a human sends "kill" command.')
    sys.exit(0)
