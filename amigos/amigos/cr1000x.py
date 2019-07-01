from pycampbellcr1000 import CR1000
from gpio import cr1000_off, cr1000_on
from time import sleep


class cr1000x:
    def finddata(self):
        cr1000_on(1)
        sleep(90)
        device = CR1000.from_url('tcp:192.168.0.30:6785')
        data = device.get_data('Public')
        # print(data[0])
        # finds strings inbetween parenthesis

        Timestamp = str(data[0]['Datetime'])
        RecNbr = str(data[0]['RecNbr'])
        Batt_volt = str(data[0]['Batt_volt'])
        Ptemp_C = str(data[0]['Ptemp_C'])
        R6 = str(data[0]['R6'])
        R10 = str(data[0]['R10'])
        R20 = str(data[0]['R20'])
        R40 = str(data[0]['R40'])
        R2_5 = str(data[0]['R2_5'])
        R4_5 = str(data[0]['R4_5'])
        R6_5 = str(data[0]['R6_5'])
        R8_5 = str(data[0]['R8_5'])
        T6 = str(data[0]['T6'])
        T10 = str(data[0]['T10'])
        T20 = str(data[0]['T20'])
        T40 = str(data[0]['T40'])
        T2_5 = str(data[0]['T2_5'])
        T4_5 = str(data[0]['T4_5'])
        T6_5 = str(data[0]['T6_5'])
        T8_5 = str(data[0]['T8_5'])
        dt = str(data[0]['DT'])
        Q = str(data[0]['Q'])
        tcdt = str(data[0]['TCDT'])
        labels = ['Timestamp', 'RecNbr', 'Batt_volt', 'Ptemp_C', 'R6', 'R10', 'R20', 'R2_5', 'R4_5',
                  'R6_5', 'R8_5', 'T6,', 'T10', 'T20', 'T40', 'T2_5', 'T4_5', 'T8_5', 'DT', 'Q', 'TCDT']
        values = [Timestamp, RecNbr, Batt_volt, Ptemp_C, R6, R10, R20, R2_5,
                  R4_5, R6_5, R8_5, T6, T10, T20, T40, T2_5, T4_5, T8_5, dt, Q, tcdt]
        return labels, values
# write to txt file

    def write_file(self):
        try:
            labels, values = self.finddata()
        except:
            pass
        else:
            therms = open(
                "/media/mmcblk0p1/amigos/amigos/logs/thermdata.log", "a+")
            for i in range(len(labels)):
                therms.write(labels[i] + ': ' + values[i] + "\n")
            therms.close()
        finally:
            cr1000_off(1)


if __name__ == "__main__":
    cr = cr1000x()
    cr.write_file()
