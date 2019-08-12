from time import sleep
from execp import printf


def read_aquadopp():
    try:
        from gpio import imm_off, imm_on
        imm_on(1)
        from serial import Serial as ser
        port = ser("/dev/ttyS4")
        port.baudrate = 9600
        port.flushInput()
        sleep(5)
        port.write("FCL\r\n")
        sleep(6)
        print(port.read(port.inWaiting()))
        port.write("FCL\r\n")
        sleep(6)
        print(port.read(port.inWaiting()))
        port.flushInput()
        sleep(3)
    except:
        printf("Imm could not connect to aquadopp")
    else:
        port.write("!00SAMPLEGETLAST\r\n")
        sleep(5)
        aquadopp_raw_data = port.read(port.inWaiting())
    finally:
        port.write("ReleaseLine\r\n")
        port.close()
        imm_off(1)
    return aquadopp_raw_data


def clean_data():
    aquadopp_raw_data = read_aquadopp()
    numbers = aquadopp_raw_data[aquadopp_raw_data.find(
        "'>")+3:aquadopp_raw_data.find("</SampleData")-2]
    aquadopp_data = numbers.split(' ')
    with open("/media/mmcblk0p1/logs/aquadopp_raw.log", "a+") as rawfile:
        rawfile.write("AD " + aquadopp_data + "\n")
    return aquadopp_data


def labeled_data():
    aquadopp_data = clean_data()
    labels = ['Month: ', 'Day: ', 'Year: ', 'Hour: ', 'Minute: ', 'Second: ', 'Error Code: ',
              'Status Code: ', 'Velocity (Beam1/X/East): ', 'Velocity (Beam2/Y/North): ',
              'Velocity (Beam3/Z/Up): ', 'Amplitude (Beam1): ', 'Amplitude (Beam2): ', 'Amplitude (Beam3): ',
              'Battery: ', 'Soundspeed: ', 'Heading: ', 'Pitch: ', 'Roll: ', 'Pressure: ', 'Temperature: ',
              'Analogue Input 1: ', 'Analogue Input 2: ', 'Speed: ', 'Direction: ']
    units = ['', '', '', '', '', '', '', '', ' m/s', ' m/s', ' m/s', ' counts', ' counts', ' counts', ' volts', ' m/s',
             ' degrees', ' degrees', ' degrees', ' dbar', ' degrees C', ' counts (0-65536)', 'counts (0-65536)',
             ' m/s', ' degrees']
    for i in range(len(aquadopp_data)):
        with open("/media/mmcblk0p1/logs/aquadopp_clean.log", "a+") as data_file:
            data_file.write(labels[i] + aquadopp_data[i] + units[i] + '\n')


def aquadopp_sbd():
    with open("/media/mmcblk0p1/logs/aquadopp_raw.log", "r") as rawfile:
        lines = rawfile.readlines()
        lastline = lines[-1]
    from monitor import backup
    backup("/media/mmcblk0p1/logs/aquadopp_raw.log", sbd=True)
    return lastline


if __name__ == "__main__":
    labeled_data()
