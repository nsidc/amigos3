import os
import shutil
from subprocess import call
from time import sleep

from execp import printf

NS = {"lseries": "http://www.witsml.org/schemas/1series"}
DTS_PULL_DELAY = 60 * 5
DTS_WIN_DATA_DIR = 'Desktop/dts_data'
DTS_RAW_DATA_DIR = "/media/mmcblk0p1/dts_data"
DTS_PROCESSED_DATA_DIR = "/media/mmcblk0p1/dts"


def metadata_filepath(filepath):
    filename = os.path.basename(filepath)
    stem = os.path.splitext(filename)[0]
    return os.path.join([DTS_PROCESSED_DATA_DIR, stem.replace(' ', '_') + '.meta'])


def data_filepath(filepath):
    filename = os.path.basename(filepath)
    stem = os.path.splitext(filename)[0]
    return os.path.join([DTS_PROCESSED_DATA_DIR, stem.replace(' ', '_') + '.csv'])


def parse_xml(filename, count):
    import xml.etree.ElementTree as ET

    tree = ET.parse(filename)
    root = tree.getroot()

    log = root.find('lseries:log')
    start_datetime = log.find('lseries:startDateTimeIndex', NS).text
    end_datetime = log.find('lseries:endDateTimeIndex', NS).text

    custom_data = log.find('lseries:customData', NS)
    acquisition_time = custom_data.find('lseries:acquisitionTime', NS).text
    reference_temp = custom_data.find('lseries:referenceTemperature', NS).text
    probe1_temp = custom_data.find('lseries:probe1Temperature ', NS).text
    probe2_temp = custom_data.find('lseries:probe2Temperature ', NS).text

    measurements = []
    logdata = log.find('lseries:logData', NS)
    for entry in logdata.findall('lseries:data', NS):
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
        means = [
            sum(values) / factor
            for values in zip(*measurements[i : (i + factor)])  # noqa
        ]
        downsampled.append(means)

    return downsampled


def write_metadata(metadata, filepath):
    with open(filepath, "w") as f:
        for k, v in metadata.iteritems():
            f.write(str(k) + '=' + str(v))


def write_data(data, filepath):
    with open(filepath, "w") as f:
        f.write("length,stokes,anti_stokes,reverse_stokes,reverse_anti_stokes,temp\n")
        for row in data:
            f.write(','.join(row) + '\n')


def update_windows_time():
    import datetime
    from ssh import SSH

    time_now = str(datetime.datetime.now()).split(".")[0]

    printf("Updating windows unit time")
    ssh = SSH("admin", "192.168.0.50")
    ssh.execute('date -s "{0}"'.format(time_now))


def acquire():
    """Entry point of DTS files retrival and execution plus time update on windows unit
    """
    from gpio import dts_on, dts_off, hub_on, hub_off
    from ssh import SSH

    printf("Turning on DTS and windows unit")
    hub_on(1)
    dts_on(1)

    printf("Sleeping {} minutes for acquisition".format(DTS_PULL_DELAY))
    sleep(DTS_PULL_DELAY)

    printf("Pulling files from windows unit")
    ssh = SSH("admin", "192.168.0.50")
    win_data_glob = os.path.join([DTS_WIN_DATA_DIR, "*"])
    ssh.copy(win_data_glob, DTS_RAW_DATA_DIR, recursive=True)

    filepaths = []
    for root, _, filenames in os.walk(DTS_RAW_DATA_DIR):
        filepaths.extend(
            [
                os.path.join([root, filename])
                for filename in filenames
                if filename.endswith('xml')
            ]
        )

    for filepath in filepaths:
        printf("Processing {}".format(filepath))
        metadata, data = parse_xml(filepath)
        write_metadata(metadata, metadata_filepath(filepath))
        write_data(metadata, data_filepath(filepath))

    printf("Syncing time on windows unit")
    update_windows_time()

    printf("Processing DTS complete, cleaning up")
    ssh.execute(["rm -rf {}".format(win_data_glob)])
    shutil.rmtree(DTS_RAW_DATA_DIR)

    hub_off(1)
    dts_off(1)


if __name__ == "__main__":
    acquire()
