import logging
import os
from bisect import bisect
from time import sleep
import xml.etree.ElementTree as ET

from honcho.tasks.common import task
from honcho.core.gpio import powered
from honcho.util import clear_directory
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.upload import queue_filepaths_chunked
from honcho.config import (
    GPIO,
    DTS_HOST,
    DTS_USER,
    DATA_DIR,
    DATA_TAGS,
    DTS_PULL_DELAY,
    DTS_WIN_DIR,
    DTS_FULL_RES_RANGES,
    DTS_CLEANUP_REMOTE,
)
from honcho.core.ssh import SSH


logger = logging.getLogger(__name__)


def ns(tag):
    return "{http://www.witsml.org/schemas/1series}" + tag


def parse_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    log = root.find(ns('log'))
    start_datetime = log.find(ns('startDateTimeIndex')).text
    end_datetime = log.find(ns('endDateTimeIndex')).text

    custom_data = log.find(ns('customData'))
    acquisition_time = custom_data.find(ns('acquisitionTime')).text
    reference_temp = custom_data.find(ns('referenceTemperature')).text
    probe1_temp = custom_data.find(ns('probe1Temperature')).text
    probe2_temp = custom_data.find(ns('probe2Temperature')).text

    measurements = []
    logdata = log.find(ns('logData'))
    for entry in logdata.findall(ns('data')):
        values = [float(el) for el in entry.text.strip().split(",")]
        measurements.append(values)

    return (
        {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'acquisition_time': acquisition_time,
            'reference_temp': reference_temp,
            'probe1_temp': probe1_temp,
            'probe2_temp': probe2_temp,
        },
        measurements,
    )


def downsample(measurements, factor=4):
    downsampled = []
    for i in range(0, len(measurements), factor):
        upper = i + factor
        window = measurements[i:upper]
        n = len(window)
        transposed = zip(*measurements[i:upper])
        means = [sum(column) / n for column in transposed]
        downsampled.append(means)

    return downsampled


def process_measurements(measurements):
    lengths = [el[0] for el in measurements]
    processed = []
    prev_index = 0
    for lower, upper in DTS_FULL_RES_RANGES:
        i_lower = bisect(lengths, lower)
        i_upper = bisect(lengths, upper)
        processed.extend(downsample(measurements[prev_index:i_lower]))
        processed.extend(measurements[i_lower:i_upper])
        prev_index = i_upper
    processed.extend(downsample(measurements[prev_index:]))

    return processed


def write(metadata, measurements, filepath):
    with open(filepath, "w") as f:
        for k, v in metadata.items():
            f.write('# ' + str(k) + '=' + str(v) + '\n')

        f.write("length,stokes,anti_stokes,reverse_stokes,reverse_anti_stokes,temp\n")
        for row in measurements:
            f.write(','.join([str(el) for el in row]) + '\n')


def query_latest(ssh, root=DTS_WIN_DIR):
    filepaths = []
    for channel in (1, 3):
        channel_dir = os.path.join(root, 'channel {0}'.format(channel))
        filepaths.append(ssh.latest_file(channel_dir))

    return filepaths


def pull_data(ssh, cleanup=DTS_CLEANUP_REMOTE):
    logger.info("Pulling files from windows unit")
    data_dir = DATA_DIR(DATA_TAGS.DTS)

    remote_filepaths = query_latest(ssh)
    for filepath in remote_filepaths:
        ssh.copy(filepath, data_dir)

    local_filepaths = [
        os.path.join(data_dir, os.path.basename(filepath))
        for filepath in remote_filepaths
    ]
    logger.info("Pulled {0} dts files".format(len(local_filepaths)))

    return local_filepaths


def process_data(filepaths):
    processed_filepaths = []
    for filepath in filepaths:
        logger.info("Processing {0}".format(filepath))
        metadata, measurements = parse_xml(filepath)
        measurements = process_measurements(measurements)
        filename = os.path.basename(filepath)
        stem = os.path.splitext(filename)[0]
        output_filepath = os.path.join(
            DATA_DIR(DATA_TAGS.DTS), stem.replace(' ', '_') + '.csv'
        )
        write(metadata, measurements, output_filepath)
        processed_filepaths.append(output_filepath)

    logger.info("Processing DTS complete")
    return processed_filepaths


def shutdown_win(ssh):
    ssh.execute("shutdown now")


@task
def execute():
    logger.info("Turning on DTS and windows unit")
    with powered([GPIO.HUB, GPIO.WIN, GPIO.DTS]):
        logger.info("Sleeping {0} seconds for acquisition".format(DTS_PULL_DELAY))
        sleep(DTS_PULL_DELAY)
        ssh = SSH(DTS_USER, DTS_HOST)
        raw_filepaths = pull_data(ssh)
        shutdown_win(ssh)

    processed_filepaths = process_data(raw_filepaths)

    tag = DATA_TAGS.DTS
    queue_filepaths_chunked(processed_filepaths, postfix=tag)
    archive_filepaths(raw_filepaths, postfix=tag)
    clear_directory(DATA_DIR(tag))
