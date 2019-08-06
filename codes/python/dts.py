from python.gpio import dts_on, dts_off  # FIX IMPORTING THESE FUNCTIONS!!
import csv
from python.excep import printf
from copy import deepcopy
import xml.etree.ElementTree as ET
from gpio import dts_off, dts_on
from time import sleep


def test():
    dts_on(1)
    sleep(60*8)
    dts_off(1)

# Sid Arora/Jack Soltys/Ryan Weatherbee
# Updated 8/2/19
# Program will read in data from DTS xml files, average the data over 2 meter lengths, and save to a csv file


# Import modules

# Function that will ssh from the windows computer into the triton board


def ssh():
    try:
        dts_on()
    except:
        printf("Not able to turn on the windows computer to run dts")
    else:
        # subprocess(ssh command and windows IP)
        pass
    finally:
        dts_off()

        # set up windows computer to automaticlly start running dts software when it boots up
        # then run ssh function to find and copy over files or just read in and output csv

# Function that needs to locate the dts channel files in the directory path/rename them


def find_files():
    # figure out how to open xml files here that automatically output from dts - or figure out how to rename the files first using python
    # use subprocess - import first too
    # rename the file so that write to csv file cleanly

    # need to first ssh in to windows comp and run the dts software and save the entire channel folder somewhere repeadedly
    # then find that folder and rename/read in all the channel data - rename to channel1.xml etc every time so function calls always work

    pass

# Function that creates tree roots of xml file and preps a csv file to be written to


def read_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    with open('test_csv_file.csv', "a+") as csvfile:
        csvfile.write(filename)
        csvfile.write('\n\n')
        csvfile.write('Date/Time START: ' + root[0][7].text)
        csvfile.write('\n\n')
        csvfile.write('Date/Time END: ' + root[0][8].text)
        csvfile.write('\n\n')
        csvfile.write('Length, stokes, anti-stokes, Temp(C)')
        csvfile.write('\n\n')
    return root

# Function that creates a 2D array of float elements


def array(filename):
    root = read_xml(filename)
    large_array = []
    for i in range(2, len(root[0][15])):
        text = root[0][15][i].text
        text = text.replace('\n', '')
        text = text.split(",")
        for i in range(0, len(text)):
            text[i] = float(text[i])
        large_array.append(text)
    return large_array, text

# Function that will average 8 0.25 meter data points into 1 data point


def average(filename):
    large_array, text = array(filename)
    zero_array = deepcopy(large_array)
    for h in range(0, len(large_array)):
        for s in range(0, len(text)):
            zero_array[h][s] = 0
    final_array = zero_array[0:(len(large_array)/8)]
    for s in range(0, len(text)):
        for h in range(0, (len(large_array)/8)):
            tem = str((large_array[8*h][s] +
                       large_array[8*h + 1][s] +
                       large_array[8*h + 2][s] +
                       large_array[8*h + 3][s] +
                       large_array[8*h + 4][s] +
                       large_array[8*h + 5][s] +
                       large_array[8*h + 6][s] +
                       large_array[8*h + 7][s])/8)
            index = tem.find(".")
            tem = tem[0:index] + tem[index:index+4]
            final_array[h][s] = float(tem)
    return final_array

# Function that writes arrays to csv - appends to bottom


def write(filename):
    final_array = average(filename)
    with open('test_csv_file.csv', "a") as csvfile:
        for i in range(0, len(final_array)):
            temp = str(final_array[i])
            endindex = temp.find("]")
            temp = temp[1:endindex]
            csvfile.write(temp)
            csvfile.write("\n")
        csvfile.write("\n\n\n")

# Function main that calls other functions and provides a filename


def main():
    write("channel1.xml")
    write("channel2.xml")


# If python script is called, the main funciton is called
if __name__ == "__main__":
    main()
