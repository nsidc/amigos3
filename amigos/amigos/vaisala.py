#Sid Arora
#6/11/19

#This Program will read in data from the Vaisala Weather Sensor in the ascii output language 
#It will read data every 5 seconds for 10 minutes straight and take the averages of each measurement
#This 10-minute data collection will repeat every hour with one line of averaged numbers sent every hour over the iridium

#Import Modules
import time 
from time import sleep
import serial
import re
import datetime
import math
#import schedule

#import coovi schedle function to run this program every hour 
#import schedule from 


def read_data():
    #Read in the weather sensor data and write to an ascii text file 
    port = serial.Serial("/dev/ttyS5")
    port.baudrate = 115200
    t=0
    #Read composite data message (all readings) every 5 seconds for 10 minutes
    while t<=600:   
        with open("weather_data_ASCII.txt","a") as raw_data:
            port.flushInput()
            data = port.readline()
            raw_data.write(data)
            sleep(5)
        t = t+5
        print(t)

def clean_data():
    #put all the mesaurements into a matrix (array of arrays)
    float_array_final = []
    string_array_final = []
    with open("weather_data_ASCII.txt","r") as f:
        for line in f:
            if "0R0" in line:
                string_array_raw = re.findall(r"[-+]?\d*\.\d+|\d+",line)
                for i in range(0,len(string_array_raw)):
                    string_array_raw[i] = float(string_array_raw[i])
                string_array_final = string_array_raw[2:]
                now = datetime.datetime.now()
                float_array_final.append(string_array_final) 
    return string_array_final,float_array_final

def average_data():
    read_data()
    string_array_final,float_array_final = clean_data()
    #average the corresponding elements and output a sinlge array of numbers 
    data_array_final = []
    for j in range(0,len(string_array_final)):
        numbers_sum = 0
        numbers_divide = 0
        for k in range(0,len(float_array_final)):
            numbers_sum = numbers_sum + float_array_final[k][j]
        numbers_divide = numbers_sum/(len(float_array_final))
        data_array_final.append(round(numbers_divide,3))

    print(data_array_final)


if __name__ == "__main__":
    average_data()


#Clear weather data ascii text file here - clears it on the amigos comp
#average the numbers from first text file into new text file here 
#write averaged data line to new text file here


#Read all data into text file over 10 mintes eery 5 seconds
#after each time do this reset large text file - put in loop 
#Then averhe and maxes and save this one line to new text file 
#send only the string of this text file over iridium - 
#every hour - keep appending this text file and send correct string number
#this text file will be back up data log in amigos box itself 

#Iridium write - when set up 
#port.write
#Read in the data from the ascii text file and average the numbers

#Send one line of just averaged numbers over iridium 