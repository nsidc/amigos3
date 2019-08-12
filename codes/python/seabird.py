from time import sleep
from execp import printf

def read_seabird_samples():
    try:
        from gpio import imm_off, imm_on
        imm_on(1)
        from serial import Serial as ser
        port = ser("/dev/ttyS4")
        port.baudrate = 9600
        port.flushInput()
        sleep(5)
        port.write("GetCD\r\n")
        sleep(5)
        port.write("GetCD\r\n")
        sleep(5)
        port.write("FCL\r\n")
        sleep(3)
        port.write("SendWakeUpTone\r\n")
        sleep(5)
        print(port.read(port.inWaiting()))
    except:
        printf("Imm could not connect to the seabird")
    else:
        port.write("#90DN6\r\n")
        seabird_raw_data = port.read(port.inWaiting())
    finally:
        port.write("ReleaseLine\r\n")
        port.close()
        imm_off(1)
    return seabird_raw_data

def clean_data():
    seabird_raw_data = read_seabird_samples()
    numbers = seabird_raw_data[seabird_raw_data.find("start time")+37:seabird_raw_data.find("<Executed/>")-1]
    numSamples = 6
    samples = numbers.split('\n')
    data = []
    for i in range(numSamples):
        data.append(samples[i].split(','))
        for j in range(3):
            data[i][j] = float(data[i][j])
    
    seabird_data = []
    totals = [0,0,0]
    for i in range(numSamples):
        totals[0] = totals[0] + data[i][0]
        totals[1] = totals[1] + data[i][1]
        totals[2] = totals[2] + data[i][2]
    seabird_data.append(totals[0]/numSamples)
    seabird_data.append(totals[1]/numSamples)
    seabird_data.append(totals[2]/numSamples)
    seabird_data.append(data[1][3])
    seabird_data.append(data[1][4][data[1][4].find(' ')+1:data[1][4].find(':')])
    #print(seabird_data)
    with open("/media/mmcblk0p1/logs/seabird_raw.log", "a+") as rawfile:
        rawfile.write("SB " + str(seabird_data) + "\n")
    return seabird_data

def labeled_data():
    seabird_data = clean_data()
    for i in range(len(seabird_data)):
        seabird_data[i] = str(seabird_data[i])
    labels = ['Temperature: ','Conductivity: ','Pressure: ','Date: ','Hour: ']
    units = [' [degrees C]',' [S/m]',' [dbar]',' [Day Month Year]','']
    for i in range(len(seabird_data)):
        with open("seabird_clean.log","a+") as labeled_data:
            labeled_data.write(labels[i] + seabird_data[i] + units[i] + '\n')


def seabird_sbd():
    with open("/media/mmcblk0p1/logs/seabird_raw.log", "r") as rawfile:
        lines = rawfile.readlines()
        lastline = lines[-1]
    from monitor import backup
    backup("/media/mmcblk0p1/logs/seabird_raw.log", sbd=True)
    return lastline


if __name__ == "__main__":
    labeled_data()
