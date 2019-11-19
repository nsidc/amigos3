import subprocess
import logging

from honcho.core.gpio import all_off

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
