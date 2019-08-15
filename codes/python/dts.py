from execp import printf
from copy import deepcopy
from time import sleep
from monitor import reschedule


def read_xml(filename):
    import xml.etree.ElementTree as ET
    tree = ET.parse(filename)
    root = tree.getroot()
    with open('/media/mmcblk0p1/dts/dts.csv', "a+") as csvfile:
        csvfile.write(filename)
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
        csvfile.write('Length(m), Stokes, Anti-stokes, Reverse-stokes, Reverse anti-stokes, Temp(C)')
        csvfile.write('\n\n')
    return root


def array(filename):
    root = read_xml(filename)
    large_array = []
    for i in range(2, len(root[0][17])):
        text = root[0][17][i].text
        text = text.replace('\n', '')
        text = text.split(",")
        for i in range(0, len(text)):
            text[i] = float(text[i])
        large_array.append(text)
    with open("/media/mmcblk0p1/logs/dts_thresholds.log","w+") as dts_file:
        boundaries = dts_file.readline()
    boundaries = boundaries.split(',')
    lower = boundaries[0]
    upper = boundaries[1]
    try:
        if lower.find('.') != -1:
            lower = float(lower)
        else:
            lower = int(lower)
        if upper.find('.') != -1:
            upper = float(lower)
        else:
            upper = int(lower)
    except:
        print('Please enter a float or an integer')
    with open('/media/mmcblk0p1/dts/dts_quarterly.csv') as quarter:
        for j in range(0,len(large_array)):
            if (large_array[j][0] - lower) >= 0 and (large_array[j][0] - upper) <= 0:
                quarter.write(large_array[j])
                quarter.write('\n')
    return large_array, text


def average(filename):
    large_array, text = array(filename)
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
            index = tem.find(".")
            tem = tem[0:index] + tem[index:index+4]
            final_array[h][s] = float(tem)
    return final_array


def write(filename):
    final_array = average(filename)
    with open('/media/mmcblk0p1/dts/dts.csv', "a") as csvfile:
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
    for root, dirs, files in walker:
        for name in files:
            path = os.path.join(root, name)
            list_file.append(path)
    return list_file


def ssh():
    try:
        from gpio import dts_on, dts_off
        dts_on(1)
        from ssh import SSH 
        ssh = SSH("admin","192.168.0.50")
        reschedule(run="ssh")
    except:
        printf("Not able to turn on the windows computer to run dts")
    else:
        printf("DTS data acquisition started")
        ssh.copy("Desktop/dts_data","/media/mmcblk0p1",recursive = True)
        array_files = list_files("/media/mmcblk0p1/dts_data")
        for index,path in enumerate(array_files):
            if array_files.find('channel 1'):
                write(path)
                break
        ssh.execute("rm -rf Desktop/dts_data")
        ssh.execute("mkdir Desktop/dts_data")
        os.rmdir('/media/mmcblk0p1/dts_data')
        printf("All done with DTS")
    finally:
        dts_off(1)



if __name__ == "__main__":
    pass