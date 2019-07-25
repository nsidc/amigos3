from pycampbellcr1000 import CR1000
from gpio import cr1000_off, cr1000_on, is_on_checker, modem_on, modem_off
from time import sleep
from execp import printf
import traceback


class cr1000x:
    def finddata(self):
        modem_on(1)
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
        labels = ['Timestamp', 'RecNbr', 'Batt_volt', 'Ptemp_C', 'R40', 'R6', 'R10', 'R20', 'R2_5', 'R4_5',
                  'R6_5', 'R8_5', 'T6,', 'T10', 'T20', 'T40', 'T2_5', 'T4_5', 'T6_5', 'T8_5', 'DT', 'Q', 'TCDT']
        values = [Timestamp, RecNbr, Batt_volt, Ptemp_C, R6, R10, R20, R2_5,
                  R4_5, R6_5, R8_5, R40, T6, T6_5, T10, T20, T40, T2_5, T4_5, T8_5, dt, Q, tcdt]
        return labels, values

    def cr_iridium(self):
        labels, values = self.finddata()
        cr_dict = {
            'BV':values[2],
            'CRT':values[3],
            'R6':values[4],
            'R10':values[5],
            'R20':values[6],
            'R40':values[11],
            'R2_5':values[7],
            'R4_5':values[8],
            'R6_5':values[9],
            'R8_5':values[10],
            'T6':values[12],
            'T10':values[14],
            'T20':values[15],
            'T40':values[16],
            'T2_5':values[17],
            'T4_5':values[18],
            'T6_5':values[13],
            'T8_5':values[19],
            'SN':values[20],
            'SNQ':values[21],
            'SNC':values[22]
        }
        return str(cr_dict)


# write to txt file

    def write_file(self):
        try:
            labels, values = self.finddata()
        except Exception as err:
            printf('Unable to acquire cr1000x data with exception {0}'.format(err))
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        else:
            therms = open(
                "/media/mmcblk0p1/logs/cr1000x.log", "a+")
            try:
                for i in range(len(labels)):
                    therms.write(labels[i] + ': ' + values[i] + "\n")
                therms.close()
            except Exception as err:
                printf(
                    'failed to format cr1000x data with exception {1}. raw data {0}'.format(values, err))
                traceback.print_exc(
                    file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        finally:
            cr1000_off(1)
            modem_off(1)

# CR1000X Live Data Reading Class


class cr1000x_live():
    def cr_read(self):
        try:
            modem_on(1)
            is_on = is_on_checker(0, 5)
            if not is_on:
                # Turn on CR1000x
                cr1000_on(1)
                sleep(15)
        except:
            printf("Problem with port or problem with power to the CR1000")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        else:
            # Read data
            device = CR1000.from_url('tcp:192.168.0.30:6785')
            data = device.get_data('Public')
        finally:
            if not is_on:
                # Turn off CR1000
                cr1000_off(1)
                modem_off(1)
        return data

    def cr_all(self):
        data = self.cr_read()
        print("Datetime: " + str(data[0]['Datetime']) + ".")
        print("Battery Voltage (V): " + str(data[0]['Batt_volt']) + ".")
        print("CR Internal Temp (C): " + str(data[0]['Ptemp_C']) + ".")
        print("Resistance 6 Meter Therm (ohm): " + str(data[0]['R6']) + ".")
        print("Resistance 10 Meter Therm (ohm): " + str(data[0]['R10']) + ".")
        print("Resistance 20 Meter Therm (ohm): " + str(data[0]['R20']) + ".")
        print("Resistance 40 Meter Therm (ohm): " + str(data[0]['R40']) + ".")
        print("Resistance 2.5 Meter Therm (ohm): " + str(data[0]['R2_5']) + ".")
        print("Resistance 4.5 Meter Therm (ohm): " + str(data[0]['R4_5']) + ".")
        print("Resistance 6.5 Meter Therm (ohm): " + str(data[0]['R6_5']) + ".")
        print("Resistance 8.5 Meter Therm (ohm): " + str(data[0]['R8_5']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data[0]['T6']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data[0]['T10']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data[0]['T20']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data[0]['T40']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data[0]['T2_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data[0]['T4_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data[0]['T6_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data[0]['T8_5']) + ".")
        print("Snow Height Distance from Ground (m): " + str(data[0]['DT']) + ".")
        print("Snow Height Quality: " + str(data[0]['Q']) + ".")
        print("Snow Height Temp Corrected Distance: " + str(data[0]['TCDT']) + ".")

    def cr_therms(self):
        data = self.cr_read()
        print("Resistance 6 Meter Therm (ohm): " + str(data[0]['R6']) + ".")
        print("Resistance 10 Meter Therm (ohm): " + str(data[0]['R10']) + ".")
        print("Resistance 20 Meter Therm (ohm): " + str(data[0]['R20']) + ".")
        print("Resistance 40 Meter Therm (ohm): " + str(data[0]['R40']) + ".")
        print("Resistance 2.5 Meter Therm (ohm): " + str(data[0]['R2_5']) + ".")
        print("Resistance 4.5 Meter Therm (ohm): " + str(data[0]['R4_5']) + ".")
        print("Resistance 6.5 Meter Therm (ohm): " + str(data[0]['R6_5']) + ".")
        print("Resistance 8.5 Meter Therm (ohm): " + str(data[0]['R8_5']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data[0]['T6']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data[0]['T10']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data[0]['T20']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data[0]['T40']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data[0]['T2_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data[0]['T4_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data[0]['T6_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data[0]['T8_5']) + ".")

    def therm6(self):
        data = self.cr_read()
        print("Resistance 6 Meter Therm (ohm): " + str(data[0]['R6']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data[0]['T6']) + ".")

    def therm10(self):
        data = self.cr_read()
        print("Resistance 10 Meter Therm (ohm): " + str(data[0]['R10']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data[0]['T10']) + ".")

    def therm20(self):
        data = self.cr_read()
        print("Resistance 20 Meter Therm (ohm): " + str(data[0]['R20']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data[0]['T20']) + ".")

    def therm40(self):
        data = self.cr_read()
        print("Resistance 40 Meter Therm (ohm): " + str(data[0]['R40']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data[0]['T40']) + ".")

    def therm2_5(self):
        data = self.cr_read()
        print("Resistance 2.5 Meter Therm (ohm): " + str(data[0]['R2_5']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data[0]['T2_5']) + ".")

    def therm4_5(self):
        data = self.cr_read()
        print("Resistance 4.5 Meter Therm (ohm): " + str(data[0]['R4_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data[0]['T4_5']) + ".")

    def therm6_5(self):
        data = self.cr_read()
        print("Resistance 6.5 Meter Therm (ohm): " + str(data[0]['R6_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data[0]['T6_5']) + ".")

    def therm8_5(self):
        data = self.cr_read()
        print("Resistance 8.5 Meter Therm (ohm): " + str(data[0]['R8_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data[0]['T8_5']) + ".")

    def snow_height(self):
        data = self.cr_read()
        print("Snow Height Distance from Ground (m): " + str(data[0]['DT']) + ".")
        print("Snow Height Quality: " + str(data[0]['Q']) + ".")
        print("Snow Height Temp Corrected Distance: " + str(data[0]['TCDT']) + ".")


if __name__ == "__main__":
    cr = cr1000x()
    cr.write_file()
