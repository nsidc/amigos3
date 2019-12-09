import subprocess
import logging

from honcho.core.gpio import all_off
from honcho.config import WATCHDOG_DEVICE

logger = logging.getLogger(__name__)


def shutdown():
    logger.info('Powering off peripherals')
    all_off()
    logger.info('Shutting down system')
    subprocess.call("shutdown -h now", shell=True)


def reboot():
    logger.info('Powering off peripherals')
    all_off()
    logger.info('Rebooting system')
    subprocess.call("reboot", shell=True)


def sleep(td):
    all_off()
    subprocess.check_call(['apmsleep', '+{0}:{1}'.format(td.hours, td.seconds)])


def watchdog_tick_3min():
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(1))
        f.write(hex(0))
        f.write(hex(1))
    logger.info('Watchdog ticked for 3 minutes')


def watchdog_tick_1hour():
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(3))
        f.write(hex(0))
        f.write(hex(3))
    logger.info('Watchdog ticked for 1 hour')
