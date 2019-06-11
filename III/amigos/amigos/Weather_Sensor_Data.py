#Arora/Jung
#5/30/19
#This Program will read in data from the Vaisala Weather Sensor in the ascii output language and translate it into readable messages

##Import Modules
import time 
import serial
import re
import datetime

from time import sleep


#Read in the weather sensor data and write to an ascii text file 
port = serial.Serial("/dev/ttyS5")
port.baudrate = 115200
t=0
<<<<<<< HEAD
while t<=100:
=======
while t<=300:
>>>>>>> e88aa55733b0ab0a1d58551c51e97346b190a3f7
    with open("weather_data_ASCII.txt","a") as raw_data:
        port.flushInput()
        data = port.readline()
        raw_data.write(data)
        sleep(5)
    t = t+5
    print(t)


#Open the file where the ascii data is saved
with open("weather_data_ASCII.txt","r") as f:
#with open("Weather_Data_Samples.txt","r") as f:
    for line in f:
        if "0R1" in line:
            string_array1 = re.findall(r"[-+]?\d*\.\d+|\d+",line)
            for i in range(0,len(string_array1)):
                string_array1[i] = float(string_array1[i])
            string_array1Final = string_array1[2:]
            now = datetime.datetime.now()
            with open("Weather_Data_Human.txt","a") as h1:
                h1.write("**Wind Data Update**\n")
                h1.write("Current Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S\n"))
                h1.write("Wind Direction Minimum (Degrees): " + str(string_array1Final[0]) + "  |  ")
                h1.write("Wind Direction Average (Degrees): " + str(string_array1Final[1]) + "  |  ")
                h1.write("Wind Direction Maximum (Degrees): " + str(string_array1Final[2]) + "  |  ")
                h1.write("Wind Speed Minimum (m/s): " + str(string_array1Final[3]) + "  |  ")
                h1.write("Wind Speed Average (m/s): " + str(string_array1Final[4]) + "  |  ")
                h1.write("Wind Speed Maximum (m/s): " + str(string_array1Final[5]) + "  |  \n\n\n")
        elif "0R2" in line:
            string_array2 = re.findall(r"[-+]?\d*\.\d+|\d+",line)
            for i in range(0,len(string_array2)):
                string_array2[i] = float(string_array2[i])
            string_array2Final = string_array2[2:]
            now = datetime.datetime.now()
            with open("Weather_Data_Human.txt","a") as h2:
                h2.write("**Pressure/Temp/Humidity Data Update**\n")
                h2.write("Current Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S\n"))
                h2.write("Air Temperature (C): " + str(string_array2Final[0]) + "  |  ")
                h2.write("Relative Humidity (%RH): " + str(string_array2Final[1]) + "  |  ")
                h2.write("Air Pressure (hPa): " + str(string_array2Final[2]) + "  |  \n\n\n")
        elif "0R3" in line:
            string_array3 = re.findall(r"[-+]?\d*\.\d+|\d+",line)
            for i in range(0,len(string_array3)):
                string_array3[i] = float(string_array3[i])
            string_array3Final = string_array3[2:]
            now = datetime.datetime.now()
            with open("Weather_Data_Human.txt","a") as h3:
                h3.write("**Precipitation Data Update**\n")
                h3.write("Current Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S\n"))
                h3.write("Rain Accumulation (mm): " + str(string_array3Final[0]) + "  |  ")
                h3.write("Rain Duration (s): " + str(string_array3Final[1]) + "  |  ")
                h3.write("Rain Intensity (mm/hour): " + str(string_array3Final[2]) + "  |  ")
                h3.write("Rain Peak Intensity (mm/hour): " + str(string_array3Final[6]) + "  |  ")
                h3.write("Hail Accumulation (hits/cm^2): " + str(string_array3Final[3]) + "  |  ")
                h3.write("Hail Duration (s): " + str(string_array3Final[4]) + "  |  ")
                h3.write("Hail Intensity (hits/cm^2/hour): " + str(string_array3Final[5]) + "  |  ")
                h3.write("Hail Peak Intensity (hits/cm^2/hour): " + str(string_array2Final[7]) + "  |  \n\n\n")
        elif "0R5" in line:
            string_array5 = re.findall(r"[-+]?\d*\.\d+|\d+",line)
            for i in range(0,len(string_array5)):
                string_array5[i] = float(string_array5[i])
            string_array5Final = string_array5[2:]
            now = datetime.datetime.now()
            with open("Weather_Data_Human.txt","a") as h5:
                h5.write("**Operational Data Update**\n")
                h5.write("Current Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S\n"))
                h5.write("Heating Temperature (C): " + str(string_array5Final[0]) + "  |  ")
                h5.write("Heating Voltage (V): " + str(string_array5Final[1]) + "  |  ")
                h5.write("Supply Voltage (V): " + str(string_array5Final[2]) + "  |  ")
                h5.write("3.5 Volts Reference Voltage (V): " + str(string_array5Final[3]) + "  |  \n\n\n")




#.write or .append
#Add all comments nicely 
#Try out with sample data, then coovi real data after live with weather sensor 
#Email ted and see what he wants from it - sve ascii on station and send to home thry iridium too?
#then translate when get home?
#confirm with ted then move on 