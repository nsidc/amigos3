# Sid Arora
# Updated as of 7/3/19

# This script will allow the user to see which devices are currently on or off

# Function to read the power log


def read_log():
    array0raw = []
    array1raw = []
    array2raw = []
    try:
        # open power log file to read
        with open("/media/mmcblk0p1/amigos/amigos/logs/power_log.log", "r") as log:
            f = log.read()
    except:
        print("Problem reading the power log file")
    else:
        # logic to create array of zero bit elements
        array0raw = list(f)
        array0final = array0raw[2:10]

        # logic to create array of first bit elements
        array1raw = list(f)
        array1final = array1raw[13:21]

        # logic to create array of second bit elements
        array2raw = list(f)
        array2final = array2raw[24:32]

    return array0final, array1final, array2final

# Function to sort the array elements into "on" or "off" arrays


def sorting():
    array0final, array1final, array2final = read_log()
    is_on_array = []
    is_off_array = []

    # eight if statements for "zero" bit array
    if array0final[0] == "1":
        pass
    else:
        pass
    if array0final[1] == "1":
        is_on_array.append("DTS/Windows is ON")
    else:
        is_off_array.append("DTS/Windows is OFF")
    if array0final[2] == "1":
        pass
    else:
        pass
    if array0final[3] == "1":
        is_on_array.append("CR1000 is ON")
    else:
        is_off_array.append("CR1000 is OFF")
    if array0final[4] == "1":
        is_on_array.append("Weather is ON")
    else:
        is_off_array.append("Weather is OFF")
    if array0final[5] == "1":
        pass
    else:
        pass
    if array0final[6] == "1":
        is_on_array.append("GPS is ON")
    else:
        is_off_array.append("GPS is OFF")
    if array0final[7] == "1":
        pass
    else:
        pass

    # eight if statements for "first" bit array
    if array1final[0] == "1":
        pass
    else:
        pass
    if array1final[1] == "1":
        pass
    else:
        pass
    if array1final[2] == "1":
        pass
    else:
        pass
    if array1final[3] == "1":
        is_on_array.append("Iridium is ON")
    else:
        is_off_array.append("Iridium is OFF")
    if array1final[4] == "1":
        is_on_array.append("Modem is ON")
    else:
        is_off_array.append("Modem is OFF")
    if array1final[5] == "1":
        is_on_array.append("Router is ON")
    else:
        is_off_array.append("Router is OFF")
    if array1final[6] == "1":
        pass
    else:
        pass
    if array1final[7] == "1":
        pass
    else:
        pass

    # eight if statements for "second" bit array
    if array2final[0] == "1":
        pass
    else:
        pass
    if array2final[1] == "1":
        pass
    else:
        pass
    if array2final[2] == "1":
        pass
    else:
        pass
    if array2final[3] == "1":
        pass
    else:
        pass
    if array2final[4] == "1":
        pass
    else:
        pass
    if array2final[5] == "1":
        pass
    else:
        pass
    if array2final[6] == "1":
        is_on_array.append("Serial is ON")
    else:
        is_off_array.append("Serial is OFF")
    if array2final[7] == "1":
        pass
    else:
        pass

    return is_on_array, is_off_array


def is_on():
    is_on_array, is_off_array = sorting()
    for i in range(len(is_on_array)):
        print(is_on_array[i])
    is_on_array = []
    is_off_array = []


def is_off():
    is_on_array, is_off_array = sorting()
    for j in range(len(is_off_array)):
        print(is_off_array[j])
    is_on_array = []
    is_off_array = []


# Main Function
if __name__ == "__main__":
    is_on()
    is_off()
