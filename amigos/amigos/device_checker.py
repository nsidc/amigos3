#Sid Arora
#Updated as of 7/1/19

#This script will allow the user to see which devices are currently on or off

#Import modules 
import re

#Function to read the power log
def read_log():
    array0raw = []
    array1raw = []
    array2raw = []
    try:
        #open power log file to read
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as log:
            f = log.read()
    except:
        print("Problem reading the power log file")
    else:
        #logic to create array of first bit elements 
        array0raw = list(f)
        array0final = array0raw[1:9]

        #logic to create array of second bit elements 
        array1raw = list(f)
        array1final = array1raw[10:18]

        #logic to create array of third bit elements 
        array2raw = list(f)
        array2final = array2raw[19:27]

    return array0final,array1final,array2final

#Function to output which modules are ON 
def is_on():
    array0final,array1final,array2final = read_log()
    #if statements for "zero" array
    if array0final[0] == "1":
        pass
    if array0final[1] == "1":
        pass
    if array0final[2] == "1":
        pass
    if array0final[3] == "1":
        print("Iridium is ON")
    if array0final[4] == "1":
        print("Modem is ON")
    if array0final[5] == "1":
        print("Router is ON")
    if array0final[6] == "1":
        pass
    if array0final[7] == "1":
        pass

    #if statements for "one" array
    if array1final[0] == "1":
        pass
    if array1final[1] == "1":
        pass
    if array1final[2] == "1":
        pass
    if array1final[3] == "1":
        print("CR is ON")
    if array1final[4] == "1":
        print("Weather is ON")
    if array1final[5] == "1":
        pass
    if array1final[6] == "1":
        print("GPS is ON")
    if array1final[7] == "1":
        pass

    #if statements for "two" array
    if array2final[0] == "1":
        pass
    if array2final[1] == "1":
        pass
    if array2final[2] == "1":
        pass
    if array2final[3] == "1":
        pass
    if array2final[4] == "1":
        pass
    if array2final[5] == "1":
        pass
    if array2final[6] == "1":
        print("Serial port is ON")
    if array2final[7] == "1":
        pass

#Function to output which modules are OFF 
def is_off():
    array0final,array1final,array2final = read_log()
    #if statements for "zero" array
    if array0final[0] == "0":
        pass
    if array0final[1] == "0":
        pass
    if array0final[2] == "0":
        pass
    if array0final[3] == "0":
        print("Iridium is OFF")
    if array0final[4] == "0":
        print("Modem is OFF")
    if array0final[5] == "0":
        print("Router is OFF")
    if array0final[6] == "0":
        pass
    if array0final[7] == "0":
        pass

    #if statements for "one" array
    if array1final[0] == "0":
        pass
    if array1final[1] == "0":
        pass
    if array1final[2] == "0":
        pass
    if array1final[3] == "0":
        print("CR is OFF")
    if array1final[4] == "0":
        print("Weather is OFF")
    if array1final[5] == "0":
        pass
    if array1final[6] == "0":
        print("GPS is OFF")
    if array1final[7] == "0":
        pass

    #if statements for "two" array
    if array2final[0] == "0":
        pass
    if array2final[1] == "0":
        pass
    if array2final[2] == "0":
        pass
    if array2final[3] == "0":
        pass
    if array2final[4] == "0":
        pass
    if array2final[5] == "0":
        pass
    if array2final[6] == "0":
        print("Serial port is OFF")
    if array2final[7] == "0":
        pass

#Main Function
if __name__ == "__main__":
    is_on()
    is_off()



#Test on amigos command line
#comment out nicely and all formatting - all comment instructions too 
#upload to my branch on git 


