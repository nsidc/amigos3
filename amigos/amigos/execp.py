import functools

import functools
from schedule import schedule as schedule
from serial import Serial as ser


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
    port = ser('/dev/ttyS3')
    port.baudrate = 115200
    port.write(message)
