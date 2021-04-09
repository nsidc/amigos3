from datetime import datetime

import honcho.tasks.supervise as supervise
from honcho.config import DATA_TAGS, DIRECTORIES_TO_MONITOR
from honcho.core.system import (CPUSample, DiskUsageSample, LoadAverageSample,
                                MemSample, ProcessSample, TopSample)


def test_is_time_for_maintenance():
    # Assert if time is maintenance hour
    # Assert if no logged success
    # Assert if only failure
    # Assert if failure more recent than success
    # Assert if last success > 1 day ago
    pass


def test_execute(mocker):
    datetime_mock = mocker.MagicMock()
    datetime_mock.now.return_value = datetime(2019, 12, 1, 0, 0, 0)
    mocker.patch("honcho.tasks.supervise.datetime", datetime_mock)

    directory_sizes_mock = mocker.MagicMock()
    directory_sizes_mock.return_value = supervise.DirectorySizeSample(
        *(i for i in enumerate(DIRECTORIES_TO_MONITOR))
    )
    mocker.patch("honcho.tasks.supervise.get_directory_sizes", directory_sizes_mock)

    measurement_counts_mock = mocker.MagicMock()
    measurement_counts_mock.return_value = supervise.TaskExecutionsSample(
        *(i for i in enumerate(DATA_TAGS))
    )
    mocker.patch(
        "honcho.tasks.supervise.get_measurement_counts", measurement_counts_mock
    )

    mocker.patch("honcho.tasks.supervise.task", lambda f: f)
    mocker.patch("honcho.tasks.orders.execute", lambda: None)
    mocker.patch("honcho.tasks.sbd.execute", lambda: None)
    mocker.patch("honcho.tasks.upload.execute", lambda: None)
    mocker.patch("honcho.tasks.archive.execute", lambda: None)

    get_top_mock = mocker.MagicMock()
    mem = MemSample(used=1, free=2, shrd=3, buff=4, cached=5)
    cpu = CPUSample(usr=1, sys=2, nic=3, idle=4, io=5, irq=6, sirq=7)
    load_average = LoadAverageSample(
        load_1=1, load_5=2, load_15=3, unknown_1=4, unknown_2=5
    )
    processes = ProcessSample(
        pid=1, ppid=2, user=3, stat=4, vsz=5, mem=6, cpu=7, command=8
    )
    get_top_mock.return_value = TopSample(
        mem=mem, cpu=cpu, load_average=load_average, processes=processes
    )
    mocker.patch("honcho.tasks.supervise.get_top", get_top_mock)

    get_disk_usage_mock = mocker.MagicMock()
    get_disk_usage_mock.return_value = [
        DiskUsageSample(
            filesystem=1, blocks=2, used=3, free=4, percent=5, mount="/media/mmcblk0p1"
        )
    ]
    mocker.patch("honcho.tasks.supervise.get_disk_usage", get_disk_usage_mock)

    mocker.patch("honcho.config.UNIT", "AMIGOSIIIA")

    log_serialized = mocker.MagicMock()
    mocker.patch("honcho.tasks.supervise.data.log_serialized", log_serialized)

    queue_sbd = mocker.MagicMock()
    mocker.patch("honcho.tasks.sbd.queue_sbd", queue_sbd)

    # TODO: mock instead (or refactor to test easier)
    # Note: cant use pyfakefs with subprocess
    try:
        supervise.execute()
    except IOError:
        pass

    # Assert collects health check
    # Assert logs health check
    # Assert queues health check SBD
    # Assert if maintenance hour runs maintenance
    # Assert ensures schedule is running
