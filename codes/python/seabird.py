from time import sleep
from execp import printf


def read_seabird_samples(ID):
    try:
        from gpio import imm_off, imm_on, enable_serial
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
        sleep(5)
        port.write("FCL\r\n")
        sleep(5)
        port.write("SendWakeUpTone\r\n")
        sleep(10)
        print(port.read(port.inWaiting()))
    except:
        printf("Imm could not connect to the seabird. Line not captured, wake up tone not sent, or poor connectivity.")
    else:
        port.write("#"+str(ID)+"DN6\r\n")
        sleep(10)
        seabird_raw_data = port.read(port.inWaiting())
    finally:
        port.write("ReleaseLine\r\n")
        port.close()
        imm_off(1)
    return seabird_raw_data


def round_3_places(num):
    num = str(num)
    if num[num.find(".")] == ".":
        num = num.split(".")
        num[1] = num[1][0:3]
        num = num[0] + '.' + num[1]
    else:
        pass
    return num


def clean_data(ID):
    try:
        seabird_raw_data = read_seabird_samples(ID)
        numbers = seabird_raw_data[seabird_raw_data.find(
            "start time")+37:seabird_raw_data.find("<Executed/>")-1]
        numSamples = 6
        samples = numbers.split('\n')
        data = []
        for i in range(numSamples):
            data.append(samples[i].split(','))
            for j in range(3):
                data[i][j] = float(data[i][j])
        seabird_data = ''
        seabird_list = []
        totals = [0, 0, 0]
        for i in range(numSamples):
            totals[0] = totals[0] + data[i][0]
            totals[1] = totals[1] + data[i][1]
            totals[2] = totals[2] + data[i][2]
        seabird_list.append(totals[0]/numSamples)
        seabird_list.append(totals[1]/numSamples)
        seabird_list.append(totals[2]/numSamples)
        seabird_list.append(data[1][3])
        seabird_list.append(data[1][4][data[1][4].find(' ')+1:data[1][4].find(':')])
        for i in range(3):
            seabird_list[i] = float(seabird_list[i])
            seabird_list[i] = round_3_places(seabird_list[i])
        for i in range(len(seabird_list)):
            seabird_data = seabird_data + str(seabird_list[i]) + ','
        with open("/media/mmcblk0p1/logs/seabird"+str(ID)+"_raw.log", "a+") as rawfile:
            rawfile.write("SB"+str(ID)+":" + str(seabird_data) + "\n")
    except:
        printf("Imm did not take data from the seabird unit " +
               str(ID) + ". Maybe poor connectivity.")
    return seabird_list


def labeled_data(ID):
    seabird_data = clean_data(ID)
    for i in range(len(seabird_data)):
        seabird_data[i] = str(seabird_data[i])
    labels = ['Temperature: ', 'Conductivity: ', 'Pressure: ', 'Date: ', 'Hour: ']
    units = [' [degrees C]', ' [S/m]', ' [dbar]', ' [Day Month Year]', '']
    for i in range(len(seabird_data)):
        with open("/media/mmcblk0p1/logs/seabird"+str(ID)+"_clean.log", "a+") as labeled_data:
            labeled_data.write(labels[i] + seabird_data[i] + units[i] + '\n')


def amigos_box_sort_SB():
    try:
        from execp import amigos_Unit
        unit = amigos_Unit
        from monitor import reschedule
        printf("Sea Bird data acquisition stated")
        if unit == "A":
            labeled_data("90")
            labeled_data("80")
        elif unit == "B":
            labeled_data("05")
            labeled_data("09")
        elif unit == "C":
            labeled_data("08")
            labeled_data("07")
            labeled_data("06")
            labeled_data("#Enter fourth Id for seabird on C - no battery unit")
        printf("Done with Sea Bird")
        reschedule(run="amigos_box_sort_SB")
    except:
        import traceback
        printf("Sea Bird failed to run")
        reschedule(re="amigos_box_sort_SB")
        traceback.print_exc(
            file=open("/media/mmcblk0p1/logs/system.log", "a+"))


def prep_sbd(ID):
    with open("/media/mmcblk0p1/logs/seabird"+str(ID)+"_raw.log", "r") as rawfile:
        lines = rawfile.readlines()
        lastline = lines[-1]
    from monitor import backup
    backup("/media/mmcblk0p1/logs/seabird"+str(ID)+"_raw.log", sbd=True)
    return lastline


def seabird_sbd():
    from execp import amigos_Unit
    unit = amigos_Unit
    lastlinetotal = []
    if unit == "A":
        lastline1 = prep_sbd("90")
        lastline2 = prep_sbd("80")
        lastlinetotal = lastline1 + lastline2
    elif unit == "B":
        lastline1 = prep_sbd("05")
        lastline2 = prep_sbd("09")
        lastlinetotal = lastline1 + lastline2
    elif unit == "C":
        lastline1 = prep_sbd("08")
        lastline2 = prep_sbd("07")
        lastline3 = prep_sbd("06")
        lastline4 = prep_sbd("#Enter fourth Id for seabird on C - no battery unit")
        # Seabird data is short enough to send all 4 seabird's data in one SBD message
        lastlinetotal = lastline1 + lastline2 + lastline3 + lastline4
    return lastlinetotal


if __name__ == "__main__":
    labeled_data("90")
