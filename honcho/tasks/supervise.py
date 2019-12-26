import os
import json
import signal
import subprocess
from datetime import datetime, timedelta
from logging import getLogger
from collections import namedtuple

from honcho.config import (
    UNIT,
    SEP,
    DATA_TAGS,
    DATA_DIR,
    DIRECTORIES_TO_MONITOR,
    START_SCHEDULE_COMMAND,
    EXECUTION_LOG_FILEPATH,
    MAINTENANCE_HOUR,
    SKIP_MAINTENANCE,
    TIMESTAMP_FMT,
)
import honcho.core.data as data
from honcho.core.sched import get_schedule_processes
from honcho.core.system import get_top, get_disk_usage

import honcho.tasks.sbd as sbd
import honcho.tasks.upload as upload
import honcho.tasks.archive as archive
import honcho.tasks.orders as orders
from honcho.tasks.common import task

logger = getLogger(__name__)

TaskExecutionsSample = namedtuple('TaskExecutionsSample', DATA_TAGS)
DirectorySizeSample = namedtuple('DirectorySizeSample', DIRECTORIES_TO_MONITOR)
HealthSample = namedtuple(
    'HealthSample',
    (
        'timestamp',
        'top',
        'disk_usage',
        'card_usage',
        'measurement_counts',
        'sbd_queue_counts',
        'directory_sizes',
    ),
)


def serialize(sample):
    serialized = SEP.join(
        [sample.timestamp.strftime(TIMESTAMP_FMT), UNIT.NAME]
        + list(str(el) for el in sample.top.mem)
        + list(str(el) for el in sample.top.cpu)
        + list(str(el) for el in sample.top.load_average)
        + list(str(el) for el in sample.card_usage)
        + list(str(el) for el in sample.measurement_counts)
        + list(str(el) for el in sample.sbd_queue_counts)
        + list(str(el) for el in sample.directory_sizes)
    )
    return serialized


def get_measurement_counts():
    return TaskExecutionsSample(
        **dict((tag, len(os.listdir(DATA_DIR(tag)))) for tag in DATA_TAGS)
    )


def get_directory_sizes():
    return DirectorySizeSample(
        **dict(
            (key, len(os.listdir(directory)))
            for key, directory in DIRECTORIES_TO_MONITOR.items()
        )
    )


def check_health():
    timestamp = datetime.now()
    top = get_top()
    disk_usage = get_disk_usage()
    card_usage = [el for el in disk_usage if el.mount == '/media/mmcblk0p1'][0]
    measurement_counts = get_measurement_counts()
    sbd_queue_counts = sbd.get_queue_counts()
    directory_sizes = get_directory_sizes()

    return HealthSample(
        timestamp=timestamp,
        top=top,
        disk_usage=disk_usage,
        card_usage=card_usage,
        measurement_counts=measurement_counts,
        sbd_queue_counts=sbd_queue_counts,
        directory_sizes=directory_sizes,
    )


def is_time_for_maintenance():
    log_filepath = EXECUTION_LOG_FILEPATH(__name__)
    if os.path.exists(log_filepath):
        with open(EXECUTION_LOG_FILEPATH(__name__), 'r') as f:
            log_data = json.load(f)
    else:
        log_data = {}

    last_success = log_data.get('last_success', None)
    if last_success is not None:
        last_success = datetime.strptime(last_success, TIMESTAMP_FMT)
    last_failure = log_data.get('last_failure', None)
    if last_failure is not None:
        last_failure = datetime.strptime(last_failure, TIMESTAMP_FMT)

    now = datetime.now()

    is_maintenance_hour = now.hour == MAINTENANCE_HOUR
    no_logged_success = last_success is None
    failed_last_time = (None not in (last_failure, last_success)) and (
        last_success < last_failure
    )
    no_success_past_day = (last_success is not None) and (
        last_success < now - timedelta(days=1)
    )

    is_time = (
        is_maintenance_hour
        or no_logged_success
        or failed_last_time
        or no_success_past_day
    ) and not SKIP_MAINTENANCE

    return is_time


def run_maintenance():
    logger.info('Performing maintenance routine')
    top = get_top()
    schedule_processes = get_schedule_processes(top)
    if schedule_processes:
        for schedule_process in schedule_processes:
            os.kill(int(schedule_process.pid), signal.SIGKILL)

    orders.execute()
    sbd.execute()
    upload.execute()
    archive.execute()


def ensure_schedule_running():
    # Start schedule if not running
    top = get_top()
    if not get_schedule_processes(top):
        logger.info('No schedule running, starting')
        subprocess.Popen([START_SCHEDULE_COMMAND], shell=True)
    else:
        logger.info('Schedule already running')


@task
def execute():
    try:
        # Health check
        health_check = check_health()
        serialized = serialize(health_check)
        data.log_serialized(serialized, DATA_TAGS.MON)
        sbd.queue_sbd(serialized, DATA_TAGS.MON)

        # If health critical:
        #         (no orders run in x days)
        #         (x failures in x days)
        #     Reboot
        #     Safe mode
        #     Attempt normal mode after x days

    finally:
        # Do daily maintenance
        if is_time_for_maintenance():
            run_maintenance()

        ensure_schedule_running()
