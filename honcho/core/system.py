import subprocess
import logging
import re
from collections import defaultdict

from honcho.core.gpio import all_off, set_awake_gpio_state
from honcho.config import WATCHDOG_DEVICE, MAX_SYSTEM_SLEEP

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


def system_standby(minutes):
    all_off()
    watchdog_tick_1hour()
    assert minutes <= MAX_SYSTEM_SLEEP
    logger.info('Sleeping for {0} minutes'.format(minutes))
    subprocess.check_call(['apmsleep', '+0:{0}'.format(minutes)])
    set_awake_gpio_state()


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


def top():
    TOP_CMD = 'top -n1'

    results = {}
    p = subprocess.Popen(
        TOP_CMD, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    output, _ = p.communicate()
    output = output.strip().split('\n')

    mem_pattern = (
        r'Mem: '
        r'(?P<used>\d+)K used, '
        r'(?P<free>\d+)K free, '
        r'(?P<shrd>\d+)K shrd, '
        r'(?P<buff>\d+)K buff, '
        r'(?P<cached>\d+)K cached'
    )
    raw = re.search(mem_pattern, output[0]).groupdict()
    results['mem'] = dict((k, int(v)) for k, v in raw.iteritems())

    cpu_pattern = (
        r'CPU:'
        r'\s+(?P<usr>\d+)% usr'
        r'\s+(?P<sys>\d+)% sys'
        r'\s+(?P<nic>\d+)% nic'
        r'\s+(?P<idle>\d+)% idle'
        r'\s+(?P<io>\d+)% io'
        r'\s+(?P<irq>\d+)% irq'
        r'\s+(?P<sirq>\d+)% sirq'
    )
    raw = re.search(cpu_pattern, output[1]).groupdict()
    results['cpu'] = dict((k, int(v)) for k, v in raw.iteritems())

    load_average_pattern = (
        r'Load average: '
        r'(?P<load_1>[\d\.]+) '
        r'(?P<load_5>[\d\.]+) '
        r'(?P<load_15>[\d\.]+) '
        r'(?P<unknown_1>[\d/]+) '
        r'(?P<unknown_2>\d+)'
    )
    raw = re.search(load_average_pattern, output[2]).groupdict()
    results['load_average'] = raw

    ps_fields = (
        ('pid', 6),
        ('ppid', 6),
        ('user', 9),
        ('stat', 6),
        ('vsz', 5),
        ('mem', 5),
        ('cpu', 5),
        ('command', 1000),
    )
    ps = defaultdict(list)
    for row in output[4:]:
        pos = 0
        for key, length in ps_fields:
            ps[key].append(row[pos : pos + length].strip())
            pos = pos + length

    results['processes'] = ps

    return results
