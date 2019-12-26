import subprocess
import logging
import re
from collections import namedtuple

from honcho.core.gpio import all_off, set_awake_gpio_state
from honcho.config import WATCHDOG_DEVICE, MAX_SYSTEM_SLEEP, KEEP_AWAKE
from honcho.util import OrderedDict

logger = logging.getLogger(__name__)

TOP_CMD = ['top', '-n', '1']
PS_CMD = ['ps']
DF_CMD = ['df']

DISK_USAGE_FIELDS = OrderedDict(
    (
        ('filesystem', 21),
        ('blocks', 10),
        ('used', 10),
        ('free', 10),
        ('percent', 5),
        ('mount', 1000),
    )
)
DiskUsageSample = namedtuple('DiskUsageSample', DISK_USAGE_FIELDS)

MEM_FIELDS = ('used', 'free', 'shrd', 'buff', 'cached')
MemSample = namedtuple('MemSample', MEM_FIELDS)

CPU_FIELDS = ('usr', 'sys', 'nic', 'idle', 'io', 'irq', 'sirq')
CPUSample = namedtuple('CPUSample', CPU_FIELDS)

LOAD_AVERAGE_FIELDS = ('load_1', 'load_5', 'load_15', 'unknown_1', 'unknown_2')
LoadAverageSample = namedtuple('LoadAverageSample', LOAD_AVERAGE_FIELDS)

PROCESS_FIELDS = OrderedDict(
    (
        ('pid', 6),
        ('ppid', 6),
        ('user', 9),
        ('stat', 6),
        ('vsz', 5),
        ('mem', 5),
        ('cpu', 5),
        ('command', 1000),
    )
)
ProcessSample = namedtuple('ProcessSample', PROCESS_FIELDS)

TopSample = namedtuple('TopSample', ('mem', 'cpu', 'load_average', 'processes'))

MEM_PATTERN = (
    r'Mem: '
    r'(?P<used>\d+)K used, '
    r'(?P<free>\d+)K free, '
    r'(?P<shrd>\d+)K shrd, '
    r'(?P<buff>\d+)K buff, '
    r'(?P<cached>\d+)K cached'
)
CPU_PATTERN = (
    r'CPU:'
    r'\s+(?P<usr>\d+)% usr'
    r'\s+(?P<sys>\d+)% sys'
    r'\s+(?P<nic>\d+)% nic'
    r'\s+(?P<idle>\d+)% idle'
    r'\s+(?P<io>\d+)% io'
    r'\s+(?P<irq>\d+)% irq'
    r'\s+(?P<sirq>\d+)% sirq'
)
LOAD_AVERAGE_PATTERN = (
    r'Load average: '
    r'(?P<load_1>[\d\.]+) '
    r'(?P<load_5>[\d\.]+) '
    r'(?P<load_15>[\d\.]+) '
    r'(?P<unknown_1>[\d/]+) '
    r'(?P<unknown_2>\d+)'
)


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
    if KEEP_AWAKE:
        logger.info('KEEP_AWAKE set, skipping sleep')
        return

    all_off()
    watchdog_tick_1hour()
    assert MAX_SYSTEM_SLEEP <= 59
    assert minutes <= MAX_SYSTEM_SLEEP
    logger.info('Sleeping for {0} minutes'.format(minutes))
    subprocess.check_call(['apmsleep', '+0:{0}'.format(minutes)])
    set_awake_gpio_state()


def watchdog_tick_3min():
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(1))
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(0))
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(1))
    logger.info('Watchdog ticked for 3 minutes')


def watchdog_tick_1hour():
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(3))
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(2))
    with open(WATCHDOG_DEVICE, 'wb') as f:
        f.write(hex(3))
    logger.info('Watchdog ticked for 1 hour')


def get_disk_usage():
    p = subprocess.Popen(DF_CMD, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = p.communicate()
    output = output.strip().split('\n')

    results = []
    for row in output[1:]:
        pos = 0
        values = {}
        for key, length in DISK_USAGE_FIELDS.items():
            end_pos = pos + length
            values[key] = row[pos:end_pos].strip()
            pos = end_pos
        results.append(DiskUsageSample(**values))

    return results


def get_ps():
    p = subprocess.Popen(PS_CMD, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = p.communicate()
    output = output.strip().split('\n')
    processes = []
    for row in output[4:]:
        pos = 0
        values = {}
        for key, length in PROCESS_FIELDS.items():
            end_pos = pos + length
            values[key] = row[pos:end_pos].strip()
            pos = pos + length
        processes.append(ProcessSample(**values))

    return processes


def get_top():
    p = subprocess.Popen(TOP_CMD, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = p.communicate()
    output = output.strip().split('\n')
    mem_sample = MemSample(**re.search(MEM_PATTERN, output[0]).groupdict())
    cpu_sample = CPUSample(**re.search(CPU_PATTERN, output[1]).groupdict())
    load_average_sample = LoadAverageSample(
        **re.search(LOAD_AVERAGE_PATTERN, output[2]).groupdict()
    )

    processes = []
    for row in output[4:]:
        pos = 0
        values = {}
        for key, length in PROCESS_FIELDS.items():
            end_pos = pos + length
            values[key] = row[pos:end_pos].strip()
            pos = pos + length
        processes.append(ProcessSample(**values))

    return TopSample(
        mem=mem_sample,
        cpu=cpu_sample,
        load_average=load_average_sample,
        processes=processes,
    )


def set_datetime(timestamp):
    subprocess.check_call(['date', '-s', timestamp.strftime('%Y-%m-%d %H:%M:%S')])
