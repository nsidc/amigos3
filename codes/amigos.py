from python.scheduler import signals, run_schedule
import traceback
from python.gpio import all_off
from python.execp import printf
import sys
try:
    # s.all_off(1)
    signals()
    run_schedule()
except Exception as err:
    printf('Scheduler failed with error message :' +
           str(err) + str(sys.exc_info()[0]) + '.' + 'Trying to restart scheduler')
    traceback.print_exc(
        file=open("/media/mmcblk0p1/logs/system.log", "a+"))
finally:
    all_off(1)
