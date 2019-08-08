from serial import Serial as ser
from time import sleep
from gpio import imm_off,imm_on
from execp import printf

def read_seabird():
    try:
        imm_on(1)
        port = ser("/dev/ttyS4")
        port.baudrate = 9600
        port.flushInput()
        port.write("GetCD\r\n")
        sleep(5)
        port.write("GetCD\r\n")
        sleep(5)
        port.write("FCL\r\n")
        sleep(3)
        port.write("SendWakeUpTone\r\n")
        sleep(5)
        #port.write (Get datetime from amigos and set it in the seabird) and set unit ID too 
        #sleep(5)
        print(port.read(port.inWaiting()))
    except:
        printf("Imm could not connect to the seabird")
    else:
        port.write("#90TS\r\n") #CHANGE TO TPS WHEN PUT IN WATER  #DN(X)6 command to upload mose recent amount of samples
        sleep(5)                            #Then average the 6 samples ourselves/put in scheduler
                                            #Figure out script for all  seabirds with different ID's too 
                                            #Fix port.read/readline to have raw data same output for labeling 
        port.write("#90DN6\r\n")
        seabird_raw_data = port.read(port.inWaiting())
    finally:
        port.write("ReleaseLine\r\n")
        port.close()
        imm_off(1)

        return seabird_raw_data

def clean_data():
    seabird_raw_data = read_seabird()
    numbers = seabird_raw_data[seabird_raw_data.find("<RemoteReply>")+22:seabird_raw_data.find("<Executed/>")-5]
    seabird_data = numbers.split(', ')
    return seabird_data

def labeled_data():
    seabird_data = clean_data()
    labels = ['Temperature: ','Conductivity: ','Pressure: ','Date: ','Time: ']
    units = [' [degrees C]',' [S/m]',' [dbar]',' [Day Month Year]',' [Hour:Minute:Second]']
    for i in range(len(seabird_data)):
        with open("/media/mmcblk0p1/logs/seabird.log","a+") as data_file:
            data_file.write(labels[i] + seabird_data[i] + units[i] + '\n')

def seabird_sbd():
    seabird_data = clean_data()
    seabird_dict = {
        'temp':seabird_data[0],
        'condct':seabird_data[1],
        'press':seabird_data[2],
        'date':seabird_data[3],
        'time':seabird_data[4]
    }
    return str(seabird_dict)

if __name__ == "__main__":
    labeled_data()