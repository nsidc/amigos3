from time import sleep
from execp import printf
import traceback


def read_aquadopp(ID):
    try:
        from gpio import imm_off, imm_on, enable_serial, disable_serial
        printf("Getting files from aquadopp {0}".format(ID))
        imm_on(1)
        enable_serial()
        sleep(10)
        from serial import Serial as ser
        port = ser("/dev/ttyS4")
        port.baudrate = 9600
        port.flushInput()
        sleep(5)
        port.write("PwrOn\r\n")
        sleep(10)
        port.write("FCL\r\n")
        sleep(6)
        port.write("FCL\r\n")
        sleep(6)
        # print(port.read(port.inWaiting()))
        port.flushInput()
        sleep(3)
    except:
        printf("Imm could not connect to aquadopp. Line not captured or connectivity error.")
    else:
        port.write("!"+str(ID)+"SAMPLEGETLAST\r\n")
        sleep(5)
        aquadopp_raw_data = port.read(port.inWaiting())
    finally:
        port.write("ReleaseLine\r\n")
        port.close()
        imm_off(1)
        disable_serial()
    return aquadopp_raw_data


def clean_data(ID):
    try:
        aquadopp_raw_data = read_aquadopp(ID)
        printf("Proccessing data for aquadopp {0}".format(ID))
        numbers = aquadopp_raw_data[aquadopp_raw_data.find(
            "'>")+3:aquadopp_raw_data.find("</SampleData")-2]
        aquadopp_list = numbers.split(' ')
        aquadopp_list.pop(4)
        aquadopp_list.pop(5)
        aquadopp_data = ''
        for i in range(len(aquadopp_list)):
            aquadopp_data = aquadopp_data + aquadopp_list[i] + ','
        with open("/media/mmcblk0p1/logs/aquadopp"+str(ID)+"_raw.log", "a+") as rawfile:
            rawfile.write("AD" + str(ID) + ":" + aquadopp_data + "\n")
    except:
        printf("Imm did not take data from the aquadopp unit " +
               str(ID) + ". Maybe poor connectivity.")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))
    return aquadopp_list


def labeled_data(ID):
    printf("Generating labels for aquadopp {0}".format(ID))
    aquadopp_data = clean_data(ID)
    labels = ['Month: ', 'Day: ', 'Year: ', 'Hour: ', 'Error Code: ',
              'Status Code: ', 'Velocity (Beam1/X/East): ', 'Velocity (Beam2/Y/North): ',
              'Velocity (Beam3/Z/Up): ', 'Amplitude (Beam1): ', 'Amplitude (Beam2): ', 'Amplitude (Beam3): ',
              'Battery: ', 'Soundspeed: ', 'Heading: ', 'Pitch: ', 'Roll: ', 'Pressure: ', 'Temperature: ',
              'Analogue Input 1: ', 'Analogue Input 2: ', 'Speed: ', 'Direction: ']
    units = ['', '', '', '', '', '', ' m/s', ' m/s', ' m/s', ' counts', ' counts', ' counts', ' volts', ' m/s',
             ' degrees', ' degrees', ' degrees', ' dbar', ' degrees C', ' counts (0-65536)', 'counts (0-65536)',
             ' m/s', ' degrees']
    for i in range(len(aquadopp_data)):
        with open("/media/mmcblk0p1/logs/aquadopp"+str(ID)+"_clean.log", "a+") as data_file:
            data_file.write(labels[i] + str(aquadopp_data[i]) + units[i] + '\n')
    with open("/media/mmcblk0p1/logs/aquadopp"+str(ID)+"_clean.log", "a+") as data_file:
        data_file.write("\n")


def amigos_box_sort_AQ():
    from execp import amigos_Unit
    unit = amigos_Unit()
    from monitor import reschedule
    printf("Started Aquadopp data acquisition")
    try:
        if unit == "A":
            labeled_data("20")
            labeled_data("21")
        elif unit == "B":
            labeled_data("22")
            labeled_data("23")
        elif unit == "C":
            labeled_data("20")
            labeled_data("21")
            # labeled_data("26")
            # labeled_data("27")
        printf("Done with aquadopp")
        reschedule(run="amigos_box_sort_AQ")
    except:
        printf("Aquadopp failed to run")
        reschedule(re="amigos_box_sort_AQ")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def prep_sbd(ID):
    with open("/media/mmcblk0p1/logs/aquadopp"+str(ID)+"_raw.log", "r") as rawfile:
        lines = rawfile.readlines()
        lastline = lines[-1]
    from monitor import backup
    backup("/media/mmcblk0p1/logs/aquadopp"+str(ID)+"_raw.log", sbd=True)
    return lastline


def aquadopp_sbd():
    from execp import amigos_Unit
    unit = amigos_Unit()
    if unit == "A":
        # When deploying box A - use these ID's when starting deployment files for two aquadopps
        lastline1 = prep_sbd("20")
        lastline2 = prep_sbd("21")
        lastlinetotal = lastline1 + lastline2
        return lastlinetotal
    elif unit == "B":
        # When deploying box B - use these ID's when starting deployment files for two aquadopps
        lastline1 = prep_sbd("22")
        lastline2 = prep_sbd("23")
        lastlinetotal = lastline1 + lastline2
        return lastlinetotal
    elif unit == "C":
        # When deploying box C - use these ID's when starting deployment files for four aquadopps
        lastline1 = prep_sbd("20")
        lastline2 = prep_sbd("21")
        # lastline3 = prep_sbd("26")
        # lastline4 = prep_sbd("27")
        lastlinetotal1 = lastline1 + lastline2
        # lastlinetotal2 = lastline3 + lastline4
        return lastlinetotal1  # lastlinetotal2


if __name__ == "__main__":
    amigos_box_sort_AQ()
