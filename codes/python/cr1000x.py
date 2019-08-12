from pycampbellcr1000 import CR1000
from gpio import cr1000_off, cr1000_on, is_on_checker, modem_on, modem_off
from time import sleep
from execp import printf, set_reschedule
import traceback
from datetime import datetime, timedelta


class cr1000x:
    def finddata(self):
        printf("Cr1000 data acquisition started")
        modem_on(1)
        cr1000_on(1)
        sleep(10)
        labels = []
        values = []
        try:
            device = CR1000.from_url('tcp:192.168.0.30:6785')
        except:
            print("Device is not on or not route to device (check the ethernet cable)")
            set_reschedule("cr1000")
            return labels, values
        printf("Connecting to CR1000x ...")
        if not device.ping_node():
            printf("No connection to CR1000x device")
            set_reschedule("cr1000")
            return
        printf("Connected ...")
        # printf("Updating device time ...")
        # start_time = device.settime(datetime.now())
        # printf("Device time set to {0}".format(start_time))
        sleep(80)
        data = device.get_raw_packets("Public")
        device.bye()
        printf("Sent bye to device")
        if data:
            data = data[0]['RecFrag'][0]['Fields']
            # print(data[0])
            # finds strings inbetween parenthesis

            Batt_volt = str(data['Batt_volt'])
            Ptemp_C = str(data['Ptemp_C'])
            R6 = str(data['R6'])
            R10 = str(data['R10'])
            R20 = str(data['R20'])
            R40 = str(data['R40'])
            R2_5 = str(data['R2_5'])
            R4_5 = str(data['R4_5'])
            R6_5 = str(data['R6_5'])
            R8_5 = str(data['R8_5'])
            T6 = str(data['T6'])
            T10 = str(data['T10'])
            T20 = str(data['T20'])
            T40 = str(data['T40'])
            T2_5 = str(data['T2_5'])
            T4_5 = str(data['T4_5'])
            T6_5 = str(data['T6_5'])
            T8_5 = str(data['T8_5'])
            dt = str(data['DT'])
            Q = str(data['Q'])
            tcdt = str(data['TCDT'])
            labels = ['Batt_volt', 'Ptemp_C', 'R40', 'R6', 'R10', 'R20', 'R2_5', 'R4_5',
                      'R6_5', 'R8_5', 'T6,', 'T10', 'T20', 'T40', 'T2_5', 'T4_5', 'T6_5', 'T8_5', 'DT', 'Q', 'TCDT']
            values = [Batt_volt, Ptemp_C, R6, R10, R20, R2_5,
                      R4_5, R6_5, R8_5, R40, T6, T6_5, T10, T20, T40, T2_5, T4_5, T8_5, dt, Q, tcdt]
        with open("/media/mmcblk0p1/logs/cr1000x_raw.log","a+") as rawfile:
            rawfile.write("CR " + values + "\n")
        return labels, values

    def cr_sbd(self):
        with open("/media/mmcblk0p1/logs/cr1000x_raw.log","r") as rawfile:
            #Take backup and read last line on the bottom and return this function 
            pass


# write to txt file

    def cr1000(self):
        try:
            labels, values = self.finddata()
            if not values:
                printf("Got a empty data clock might have shift on device. Will try again")
                set_reschedule("cr1000")
        except Exception as err:
            set_reschedule("cr1000")
            printf(
                'Unable to acquire cr1000x data with exception {0}``\\_(^/)_/``'.format(err))
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        else:
            therms = open(
                "/media/mmcblk0p1/logs/cr1000x_clean.log", "a+")
            try:
                for i in range(len(labels)):
                    therms.write(labels[i] + ': ' + values[i] + "\n")
                therms.close()
            except Exception as err:
                set_reschedule("cr1000")
                printf(
                    'failed to format cr1000x data with exception {1}``\\_(^/)_/``'.format(values))
                traceback.print_exc(
                    file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            printf("Cr1000 data acquisition done :)")
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
                sleep(10)
        except:
            printf("Problem with port or problem with power to the CR1000")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        else:
            # Read data
            try:
                device = CR1000.from_url('tcp:192.168.0.30:6785')
            except:
                print("Device is not on or no route to device (maybe check the ethernet cable)")
                exit(0)
            print("Connecting to CR1000x ...")
            if not device.ping_node():
                print("No connection to CR1000x device")
                return
            print("Connected ...")
            sleep(10)
            data = device.get_raw_packets("Public")
            # device.settime(datetime.now())
            if data:
                data = data[0]['RecFrag'][0]['Fields']
            return data
        finally:
            if not is_on:
                # Turn off CR1000
                cr1000_off(1)
                modem_off(1)

    def cr_all(self):
        data = self.cr_read()
        print("Battery Voltage (V): " + str(data['Batt_volt']) + ".")
        print("CR Internal Temp (C): " + str(data['Ptemp_C']) + ".")
        print("Resistance 6 Meter Therm (ohm): " + str(data['R6']) + ".")
        print("Resistance 10 Meter Therm (ohm): " + str(data['R10']) + ".")
        print("Resistance 20 Meter Therm (ohm): " + str(data['R20']) + ".")
        print("Resistance 40 Meter Therm (ohm): " + str(data['R40']) + ".")
        print("Resistance 2.5 Meter Therm (ohm): " + str(data['R2_5']) + ".")
        print("Resistance 4.5 Meter Therm (ohm): " + str(data['R4_5']) + ".")
        print("Resistance 6.5 Meter Therm (ohm): " + str(data['R6_5']) + ".")
        print("Resistance 8.5 Meter Therm (ohm): " + str(data['R8_5']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data['T6']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data['T10']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data['T20']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data['T40']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data['T2_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data['T4_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data['T6_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data['T8_5']) + ".")
        print("Snow Height Distance from Ground (m): " + str(data['DT']) + ".")
        print("Snow Height Quality: " + str(data['Q']) + ".")
        print("Snow Height Temp Corrected Distance: " + str(data['TCDT']) + ".")

    def cr_therms(self):
        data = self.cr_read()
        print("Resistance 6 Meter Therm (ohm): " + str(data['R6']) + ".")
        print("Resistance 10 Meter Therm (ohm): " + str(data['R10']) + ".")
        print("Resistance 20 Meter Therm (ohm): " + str(data['R20']) + ".")
        print("Resistance 40 Meter Therm (ohm): " + str(data['R40']) + ".")
        print("Resistance 2.5 Meter Therm (ohm): " + str(data['R2_5']) + ".")
        print("Resistance 4.5 Meter Therm (ohm): " + str(data['R4_5']) + ".")
        print("Resistance 6.5 Meter Therm (ohm): " + str(data['R6_5']) + ".")
        print("Resistance 8.5 Meter Therm (ohm): " + str(data['R8_5']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data['T6']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data['T10']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data['T20']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data['T40']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data['T2_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data['T4_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data['T6_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data['T8_5']) + ".")

    def therm6(self):
        data = self.cr_read()
        print("Resistance 6 Meter Therm (ohm): " + str(data['R6']) + ".")
        print("Temperature 6 Meter Therm (C): " + str(data['T6']) + ".")

    def therm10(self):
        data = self.cr_read()
        print("Resistance 10 Meter Therm (ohm): " + str(data['R10']) + ".")
        print("Temperature 10 Meter Therm (C): " + str(data['T10']) + ".")

    def therm20(self):
        data = self.cr_read()
        print("Resistance 20 Meter Therm (ohm): " + str(data['R20']) + ".")
        print("Temperature 20 Meter Therm (C): " + str(data['T20']) + ".")

    def therm40(self):
        data = self.cr_read()
        print("Resistance 40 Meter Therm (ohm): " + str(data['R40']) + ".")
        print("Temperature 40 Meter Therm (C): " + str(data['T40']) + ".")

    def therm2_5(self):
        data = self.cr_read()
        print("Resistance 2.5 Meter Therm (ohm): " + str(data['R2_5']) + ".")
        print("Temperature 2.5 Meter Therm (C): " + str(data['T2_5']) + ".")

    def therm4_5(self):
        data = self.cr_read()
        print("Resistance 4.5 Meter Therm (ohm): " + str(data['R4_5']) + ".")
        print("Temperature 4.5 Meter Therm (C): " + str(data['T4_5']) + ".")

    def therm6_5(self):
        data = self.cr_read()
        print("Resistance 6.5 Meter Therm (ohm): " + str(data['R6_5']) + ".")
        print("Temperature 6.5 Meter Therm (C): " + str(data['T6_5']) + ".")

    def therm8_5(self):
        data = self.cr_read()
        print("Resistance 8.5 Meter Therm (ohm): " + str(data['R8_5']) + ".")
        print("Temperature 8.5 Meter Therm (C): " + str(data['T8_5']) + ".")

    def snow_height(self):
        data = self.cr_read()
        print("Snow Height Distance from Ground (m): " + str(data['DT']) + ".")
        print("Snow Height Quality: " + str(data['Q']) + ".")
        print("Snow Height Temp Corrected Distance: " + str(data['TCDT']) + ".")


if __name__ == "__main__":
    cr = cr1000x()
    cr.write_file()
