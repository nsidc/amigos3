from serial import Serial as ser
from time import sleep
from gpio import imm_off,imm_on
from execp import printf

def read_aquadopp():
    try:
        imm_on(1)
        port = ser("/dev/ttyS4")
        port.baudrate = 9600
        port.flushInput()
        sleep(5)
        port.write("CaptureLine\r\n")
        sleep(6)
        print(port.read(port.inWaiting()))
        port.write("CaptureLine\r\n")
        sleep(6)
        print(port.read(port.inWaiting()))
        port.flushInput()
        sleep(3)
        #port.write("!00SampleGetList\r\n")


        #SAMPLEGETLAST command - use in place of getting sample number and all - no need to erase anymore 


        # for both sensors - have if statement to check CL command line - not FCL - 
        # then release line after every session

        sleep(5)
        
        #summary = port.read(port.inWaiting())
        port.flushInput()
        #print("The following newest sample will be recorded: " + summary[73:81])
        port.flushInput()
        sleep(3)
    except:
        printf("Imm could not connect to aquadopp")
    else:
        ##port.write("!00SAMPLEGETLAST\r\n")

        port.write("!00SAMPLEGETDATA:" + summary[73:81] + "\r\n")
        sleep(5) 
        aquadopp_raw_data = port.read(port.inWaiting())
        #port.flushInput()
        #sleep(3) 
    finally:
        #port.write("!00SampleEraseAll\r\n")  #try not to have erase anything - just have file wrapping to keep most recent 16000k of data 
        #port.close()
        #imm_off(1)
    #print(aquadopp_raw_data)
    return aquadopp_raw_data

def clean_data():
    aquadopp_raw_data = read_aquadopp()
    numbers = aquadopp_raw_data[aquadopp_raw_data.find("'>")+3:aquadopp_raw_data.find("</SampleData")-2]
    aquadopp_data = numbers.split(' ')
    return aquadopp_data

def labeled_data():
    aquadopp_data = clean_data()
    labels = ['Month: ','Day: ','Year: ','Hour: ','Minute: ','Second: ','Error Code: ',
        'Status Code: ','Velocity (Beam1/X/East): ','Velocity (Beam2/Y/North): ',
        'Velocity (Beam3/Z/Up): ','Amplitude (Beam1): ','Amplitude (Beam2): ','Amplitude (Beam3): ',
        'Battery: ','Soundspeed: ','Heading: ','Pitch: ','Roll: ','Pressure: ','Temperature: ',
        'Analogue Input 1: ','Analogue Input 2: ', 'Speed: ','Direction: ']
    units = ['','','','','','','','',' m/s',' m/s',' m/s',' counts',' counts',' counts',' volts',' m/s',
        ' degrees',' degrees',' degrees',' dbar', ' degrees C',' counts (0-65536)','counts (0-65536)',
        ' m/s',' degrees']
    for i in range(len(aquadopp_data)):
        with open("/media/mmcblk0p1/logs/aquadopp.log","a+") as data_file:
            data_file.write(labels[i] + aquadopp_data[i] + units[i] + '\n')

def aquadopp_sbd():
    aquadopp_data = clean_data()
    aquadopp_dict = {
        'm':aquadopp_data[0],
        'd':aquadopp_data[1],
        'y':aquadopp_data[2],
        'hr':aquadopp_data[3],
        'mi':aquadopp_data[4],
        's':aquadopp_data[5],
        'ec':aquadopp_data[6],
        'sc':aquadopp_data[7],
        'v1':aquadopp_data[8],
        'v2':aquadopp_data[9],
        'v3':aquadopp_data[10],
        'a1':aquadopp_data[11],
        'a2':aquadopp_data[12],
        'a3':aquadopp_data[13],
        'bt':aquadopp_data[14],
        'ss':aquadopp_data[15],
        'he':aquadopp_data[16],
        'pi':aquadopp_data[17],
        'ro':aquadopp_data[18],
        'p':aquadopp_data[19],
        't':aquadopp_data[20],
        'ai1':aquadopp_data[21],
        'ai2':aquadopp_data[22],
        'sp':aquadopp_data[23],
        'dir':aquadopp_data[24]
    }
    return str(aquadopp_dict)

if __name__ == "__main__":
    labeled_data()


