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
        port.write("#90TS\r\n") 
        sleep(5)
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
    with open("/media/mmcblk0p1/logs/seabird_raw.log","a+") as rawfile:
        rawfile.write("SB " + seabird_data + "\n")
    return seabird_data

def labeled_data():
    seabird_data = clean_data()
    labels = ['Temperature: ','Conductivity: ','Pressure: ','Date: ','Time: ']
    units = [' [degrees C]',' [S/m]',' [dbar]',' [Day Month Year]',' [Hour:Minute:Second]']
    for i in range(len(seabird_data)):
        with open("/media/mmcblk0p1/logs/seabird_clean.log","a+") as data_file:
            data_file.write(labels[i] + seabird_data[i] + units[i] + '\n')

def seabird_sbd():
    with open("/media/mmcblk0p1/logs/seabird_raw.log","r") as rawfile:
        lines = rawfile.readlines()
        lastline = lines[-1]
    backup("/media/mmcblk0p1/logs/seabird_raw.log",sbd = True)
    return lastline

if __name__ == "__main__":
    labeled_data()