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

#import coovi schedle function to run this program every hour 
#import schedule from 



#Read in the weather sensor data and write to an ascii text file 
port = serial.Serial("/dev/ttyS5")
port.baudrate = 115200
t=0
#Read composite data message (all readings) every 5 seconds for 10 minutes
while t<=300:  #change to 600 seconds after test!! 
    with open("weather_data_ASCII.txt","a") as raw_data:
        port.flushInput()
        data = port.readline()
        raw_data.write(data)
        sleep(5)
    t = t+5
    print(t)
#Clear weather data ascii text file here
#average the numbers from first text file into new text file here 
#write averaged data line to new text file here


#Read all data into text file over 10 mintes eery 5 seconds
#after each time do this reset large text file - put in loop 
#Then averhe and maxes and save this one line to new text file 
#send only the string of this text file over iridium - 
#every hour - keep appending this text file and send correct string number
#this text file will be back up data log in amigos box itself 

#Print (ave var) - for now??
#Iridium write - when set up 
#port.write
#Read in the data from the ascii text file and average the numbers

#Send one line of just averaged numbers over iridium 