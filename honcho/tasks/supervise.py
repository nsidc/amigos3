import os
import signal
import subprocess
from datetime import datetime
from logging import getLogger
from collections import namedtuple

from honcho.config import (
    UNIT,
    SEP,
    DATA_TAGS,
    DATA_DIR,
    SBD_QUEUE_DIR,
    UPLOAD_QUEUE_DIR,
    DIRECTORIES_TO_MONITOR,
    START_NORMAL_SCHEDULE_SCRIPT,
    MAINTENANCE_HOUR,
    TIMESTAMP_FMT,
)
import honcho.core.data as data
from honcho.core.system import get_top, get_disk_usage

from honcho.tasks.sbd import queue_sbd
import honcho.tasks.archive as archive
import honcho.tasks.orders as orders
from honcho.util import log_execution

logger = getLogger(__name__)

MeasurementsCountSample = namedtuple('MeasurementsCountSample', DATA_TAGS)
SBDQueueCountSample = namedtuple('SBDQueueCountSample', DATA_TAGS)
UploadQueueCountSample = namedtuple('UploadQueueCountSample', 'files')
DirectorySizeSample = namedtuple('DirectorySizeSample', DIRECTORIES_TO_MONITOR)


def serialize(
    timestamp, top, card_usage, measurement_counts, sbd_queue_counts, directory_sizes
):
    serialized = SEP.join(
        [timestamp.strftime(TIMESTAMP_FMT), UNIT]
        + top.mem
        + top.cpu
        + top.load_average
        + card_usage
        + measurement_counts
        + sbd_queue_counts
        + directory_sizes
    )
    return serialized


def check_schedule(top):
    schedule_processes = [
        sample for sample in top.processes if 'schedule --execute' in sample.command
    ]
    if len(schedule_processes) > 1:
        raise Exception('Multiple schedule processes running')
    elif len(schedule_processes) == 1:
        return schedule_processes[0]
    else:
        return None


def get_measurement_counts():
    return MeasurementsCountSample(
        **dict((tag, len(os.listdir(DATA_DIR(tag)))) for tag in DATA_TAGS)
    )


def get_sbd_queue_counts():
    return SBDQueueCountSample(
        **dict((tag, len(os.listdir(SBD_QUEUE_DIR(tag)))) for tag in DATA_TAGS)
    )


def get_upload_queue_count():
    return UploadQueueCountSample(os.listdir(UPLOAD_QUEUE_DIR))


def get_directory_sizes():
    return DirectorySizeSample(
        **dict(
            (os.path.basename(directory), len(os.listdir(directory)))
            for directory in DIRECTORIES_TO_MONITOR
        )
    )


@log_execution
def execute():
    # Health check
    timestamp = datetime.now()
    top = get_top()
    schedule_process = check_schedule(top)
    disk_usage = get_disk_usage()
    card_usage = [el for el in disk_usage if el.mount == '/media/mmcblk0p1'][0]
    measurement_counts = get_measurement_counts()
    sbd_queue_counts = get_sbd_queue_counts()
    directory_sizes = get_directory_sizes()
    serialized = serialize(
        timestamp,
        top,
        card_usage,
        measurement_counts,
        sbd_queue_counts,
        directory_sizes,
    )
    data.log_serialized(serialized, DATA_TAGS.MON)
    queue_sbd(DATA_TAGS.MON, serialized)

    # If health critical
    #     Reboot
    #     Safe mode

    # Do daily maintenance
    if timestamp.hour == MAINTENANCE_HOUR:
        os.kill(schedule_process['pid'], signal.SIGKILL)
        archive.execute()
        orders.execute()

    # Start schedule if not running
    top_sample = get_top()
    if check_schedule(top_sample) is None:
        subprocess.Popen([START_NORMAL_SCHEDULE_SCRIPT], shell=True)


if __name__ == '__main__':
    execute()
