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
from schedule import schedule as schedule
from gpio import weather_on
from gpio import weather_off

def read_data():
    try:
        #Turn on Weather Station
        weather_on(1)
        sleep(10)
        #Read in the weather sensor data and write to an ascii text file 
        port = serial.Serial("/dev/ttyS5")
        port.baudrate = 115200
    except:
        print("Could not turn on Vaisala")
    else:
        t=0
        #Read composite data message (all readings) every 10 seconds for 2 minutes
        while t<=120:   
            with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt","a") as raw_data:
                port.flushInput()
                data = port.readline()
                raw_data.write(data)
                sleep(10)
            t = t+10
            print(t)
    finally:
        #Turn off Weather Station
        weather_off(1)

def clean_data():
    #put all the mesaurements into a matrix (array of arrays)
    float_array_final = []
    string_array_final = []
    with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt","r") as f:
        for line in f:
            if "0R0" in line:
                string_array_raw = re.findall(r"[-+]?\d*\.\d+|\d+",line)
                for i in range(0,len(string_array_raw)):
                    string_array_raw[i] = float(string_array_raw[i])
                string_array_final = string_array_raw[2:]
                float_array_final.append(string_array_final) 
    return string_array_final,float_array_final

def average_data():
    #Call first two functions in correct order 
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
    #Write the averaged array elements to a text file - append
    now = datetime.datetime.now()
    with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_hourly.txt","a") as hourly:
        hourly.write("Current Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S\n"))
        hourly.write("Wind Direction Average (Degrees): " + str(data_array_final[0]) + ".\n")
        hourly.write("Wind Speed Average (m/s): " + str(data_array_final[1]) + ".\n")
        hourly.write("Air Temperature (C): " + str(data_array_final[2]) + ".\n")
        hourly.write("Relative Humidity (%RH): " + str(data_array_final[3]) + ".\n")
        hourly.write("Air Pressure (hPa): " + str(data_array_final[4]) + ".\n")
        hourly.write("Rain Accumulation (mm): " + str(data_array_final[5]) + ".\n")
        hourly.write("Rain Duration (s): " + str(data_array_final[6]) + ".\n")
        hourly.write("Rain Intensity (mm/h): " + str(data_array_final[7]) + ".\n")
        hourly.write("Rain Peak Intensity (mm/h): " + str(data_array_final[11]) + ".\n")
        hourly.write("Hail Accumulation (hits/cm^2): " + str(data_array_final[8]) + ".\n")
        hourly.write("Hail Duration (s): " + str(data_array_final[9]) + ".\n")
        hourly.write("Hail Intensity (hits/cm^2/hour): " + str(data_array_final[10]) + ".\n")
        hourly.write("Hail Peak Intensity (hits/cm^2/hour): " + str(data_array_final[12]) + ".\n")
        hourly.write("Vaisala Heating Temperature (C): " + str(data_array_final[13]) + ".\n")
        hourly.write("Vaisala Heating Voltage (V): " + str(data_array_final[14]) + ".\n")
        hourly.write("Vaisala Supply Voltage (V): " + str(data_array_final[15]) + ".\n\n\n")
    #Clear the ascii data file to be used again to read fresh data next hour 
    open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ascii.txt","w").close()

def vaisala_schedule():
    vaisala = schedule.Scheduler()
    #Perform this measurement reading every hour between :58 to :00
    vaisala.every().hours.at(":58").do(average_data)
    while True:
        vaisala.run_pending()
        sleep(1)



if __name__ == "__main__":
    vaisala_schedule()