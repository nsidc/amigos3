import python.scheduler as s
import traceback
from python.gpio import all_off
import sys
try:
    s.signals()
    s.modem_on(1)
    s.run_schedule()
except Exception as err:
    s.printf('Scheduler failed with error message :' +
             str(err) + str(sys.exc_info()[0]) + '\n' + 'Trying to restart scheduler')
    traceback.print_exc(
        file=open("/media/mmcblk0p1/logs/system.log", "a+"))
finally:
    all_off(1)
