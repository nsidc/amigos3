from execp import printf
from copy import deepcopy
from time import sleep
from monitor import reschedule
import traceback
from subprocess import call

para = [False]


def read_xml(filename, count):
    """[summary]

    Arguments:
        filename {[type]} -- [description]
        count {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(filename)
    root = tree.getroot()
    with open('/media/mmcblk0p1/dts/dts{0}.csv'.format(count), "a+") as csvfile:
        csvfile.write(filename.split("/")[-1])
        csvfile.write('\n\n')
        csvfile.write('Date/Time START: ' + root[0][7].text)
        csvfile.write('\n\n')
        csvfile.write('Date/Time END: ' + root[0][8].text)
        csvfile.write('\n\n')
        csvfile.write('Acquisition Time: ' + root[0][18][0].text)
        csvfile.write('\n\n')
        csvfile.write('Reference Temp: ' + root[0][18][1].text)
        csvfile.write('\n\n')
        csvfile.write('Probe Temp 1: ' + root[0][18][2].text)
        csvfile.write('\n\n')
        csvfile.write('Probe Temp 2: ' + root[0][18][3].text)
        csvfile.write('\n\n')
        csvfile.write(
            'Length(m), Stokes, Anti-stokes, Reverse-stokes, Reverse anti-stokes, Temp(C)')
        csvfile.write('\n\n')
    return root


def reset_clock():
    """Reset flag for DTS schedule update
    """
    para[0] = False


def array(filename, count):
    """[summary]

    Arguments:
        filename {[type]} -- [description]
        count {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    root = read_xml(filename, count)
    large_array = []
    for i in range(2, len(root[0][17])):
        text = root[0][17][i].text
        text = text.replace('\n', '')
        text = text.split(",")
        for i in range(0, len(text)):
            text[i] = float(text[i])
        large_array.append(text)
    try:
        with open("/media/mmcblk0p1/logs/dts_thresholds.log", "r") as dts_file:
            boundaries = dts_file.readline()
        boundaries = boundaries.split(',')

        lower = boundaries[0]
        upper = boundaries[1]
        if lower.find('.') != -1:
            lower = float(lower)
        else:
            lower = int(lower)
        if upper.find('.') != -1:
            upper = float(lower)
        else:
            upper = int(lower)
    except:
        upper = 200
        lower = 0
    with open('/media/mmcblk0p1/dts/dts_quarterly{0}.csv'.format(count), "a+") as quarter:
        for j in range(0, len(large_array)):
            if (large_array[j][0] - lower) >= 0 and (large_array[j][0] - upper) <= 0:
                quarter.write(str(large_array[j])[1:-2])
                quarter.write('\n')
    return large_array, text


def average(filename, count):
    """[summary]

    Arguments:
        filename {[type]} -- [description]
        count {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    try:
        large_array, text = array(filename, count)
        zero_array = deepcopy(large_array)
        for h in range(0, len(large_array)):
            for s in range(0, len(text)):
                zero_array[h][s] = 0
        final_array = zero_array[0:(len(large_array)/4)]
        for s in range(0, len(text)):
            for h in range(0, (len(large_array)/4)):
                tem = str((large_array[4*h][s] +
                           large_array[4*h + 1][s] +
                           large_array[4*h + 2][s] +
                           large_array[4*h + 3][s])/4)
                try:
                    index = tem.find(".")
                    tem = tem[0:index] + tem[index:index+4]
                    final_array[h][s] = float(tem)
                except:
                    try:
                        tem = str((large_array[4*h][s] +
                                   large_array[4*h + 1][s] +
                                   large_array[4*h + 2][s] +
                                   large_array[4*h + 3][s])/4)
                        tem = tem[0:index] + tem[index:]
                        final_array[h][s] = float(tem)
                    except:
                        printf("Failed to process dts data")
                        traceback.print_exc(
                            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        return final_array
    except:
        printf("Failed to process dts data")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def write(filename, count):
    """[summary]

    Arguments:
        filename {[type]} -- [description]
        count {[type]} -- [description]
    """
    final_array = average(filename, count)
    with open('/media/mmcblk0p1/dts/dts{0}.csv'.format(count), "a+") as csvfile:
        for i in range(0, len(final_array)):
            temp = str(final_array[i])
            endindex = temp.find("]")
            temp = temp[1:endindex]
            csvfile.write(temp)
            csvfile.write("\n")
        csvfile.write("\n\n\n")


def list_files(folder):
    """List files in a directory recursively

    Arguments:
        folder {string} -- Path to the base directory

    Returns:
        [List] -- List of all file
    """
    import os
    walker = os.walk(folder)
    list_file = []
    list_dirs = []
    printf("Listing total files from channel 1 and 3")
    for root, dirs, files in walker:
        for name in files:
            path = os.path.join(root, name)
            list_file.append(path)
        for name in dirs:
            path = os.path.join(root, name)
            list_dirs.append(path)
    printf("A total of {0} found from copied folder".format(len(list_file)))
    return list_dirs, list_file


def get_dts_time():
    """Read the DTS time from a log file

    Returns:
        [str] -- Time of last run of DTS
    """
    with open("/media/mmcblk0p1/logs/dts_time", "r") as d_time:
        dts_time = d_time.read()
    return dts_time


def update_win_time():
    """Update windows unit time
    """
    import datetime
    time_now = str(datetime.datetime.now()).split('.')[0]
    from ssh import SSH
    printf("Updating Windows unit time")
    ssh = SSH("admin", "192.168.0.50")
    ssh.execute('date -s "{0}"'.format(time_now))


def ssh():
    """Entry point of DTS files retrival and execution plus time update on windows unit
    """
    try:
        from gpio import dts_on, dts_off, modem_on, modem_off
        printf("DTS data acquisition started")
        modem_on(1)
        dts_on(1)
        sleep(15*60)
        count = 0
        from ssh import SSH
        ssh = SSH("admin", "192.168.0.50")
        printf("Copying files over from windows Unit")
        ssh.copy("Desktop/dts_data", "/media/mmcblk0p1", recursive=True)
        array_dirs, array_files = list_files("/media/mmcblk0p1/dts_data")
        update_win_time()
        if para[0] is True:
            printf("Have already tried to update dts schedule. Will try again after time reset")
            dts_off(1)
            modem_off(1)
        try:
            printf("Getting the last date of file drop from DTS")
            path_win = "/".join(array_dirs[2].split("/")[3:])
            dts_time = ssh.execute(
                'date -r Desktop/{0} "+%YH%mH%dH%HH%MH%S"'.format(path_win))
            dts_time = dts_time[0].replace("\n", "")
            with open("/media/mmcblk0p1/logs/dts_time", "w+") as d_time:
                d_time.write(str(dts_time))
            printf("Time stamp saved :)")
        except:
            if para[0] is False:
                printf(
                    "Not DTS data available on the Window Unit. Keeping the unit on for one cycle per 24h")
                traceback.print_exc(
                    file=open("/media/mmcblk0p1/logs/system.log", "a+"))
                para[0] = True
    except:
        printf("Not able to turn on the windows computer to run dts")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    else:
        # print(re)
        if array_files:
            printf("Start processing files from Channel 1 only")
        try:
            for index, path in enumerate(array_files):
                if path.find('channel 1') != -1:
                    write(path, count)
                    count = count+1
            printf("Files processing is done successfully :)")
        except:
            printf("Oouch, an error occurs while processing DTS data")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            return
        ssh.execute(["rm -rf Desktop/dts_data", "mkdir Desktop/dts_data"])
        # print(out)
        count = 0
        call('rm -rf /media/mmcblk0p1/dts_data', shell=True)
        printf("Removed copied files from Win unit and Tritron")
        printf("All done with DTS :)")
    finally:
        if not para[0]:
            reschedule(run="ssh")
            dts_off(1)
            modem_off(1)


if __name__ == "__main__":
    ssh()
