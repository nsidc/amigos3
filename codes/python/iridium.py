from serial import Serial as ser
from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
from time import sleep
from execp import printf, set_reschedule, welcome
from ftplib import FTP
import os
from time import sleep
from monitor import backup
import traceback
from subprocess import call, Popen, PIPE
from execp import amigos_Unit

from solar import solar_live
from vaisala import Average_Reading
from cr1000x import cr1000x
from seabird import seabird_sbd
from aquadopp import aquadopp_sbd


class dial():
    def __init__(self, *args, **kwargs):
        self.username = "amigos3"
        self.pwd = "zaehoD1a"
        self.hostname = "128.138.135.165"
        self.router_host = "http://192.168.0.1:8080/cgi-bin/menuform.cgi?"
        self.router_config = "ppp1_local_ip=192.168.0.1&ppp1_remote_ip=192.168.0.90&ppp1_override_remote_ip=enable"
        self.router_confirm = "form=form_activate_config"
        self.router_auth = ("admin", "")
        self.default_path = "/media/mmcblk0p1/"

    def test_connection(self):
        ftp = None
        try:
            ftp = FTP(self.hostname)
        except:
            print("FTP connection failed. Trying once more :(")
            try:
                ftp = FTP(self.hostname)
            except:
                pass
        try:
            welcome = ftp.getwelcome()
        except:
            set_reschedule("Out")
            print("Can not connect to server 128.138.135.165. Will try later :(")
            if ftp is not None:
                return ftp
            return None
        else:
            printf("Server sent a greeting :)")
            greeting = None
            try:
                welcome = welcome[welcome.find("*****"): welcome.find(" *** ")]
                greeting = []
                greeting = greeting.append(welcome)
            except:
                set_reschedule("Out")
            if greeting is not None:
                printf(greeting)
            return ftp
        return None

    def compress_file(self, file_name, own=False):
        # if own is True:
        #     # print(file_name)
        try:
            folder_name = file_name
            if os.path.isfile(file_name):
                folder_name = file_name.replace(".log", '')
            # print(folder_name, file_name)
            unit = amigos_Unit()
            printf("zipping file ")
            # call("tar czf {0} {1}".format(folder_name+".tar.gz", file_name), shell=True)
            p = Popen("tar czf {0} {1}".format(folder_name+"{0}.tar.gz".format(unit), file_name),
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            out = p.communicate()
            # print(out)
            sleep(2)
            return folder_name+"{0}.tar.gz".format(unit)
        except:
            set_reschedule("Out")
            printf("zipping failed :(")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            return None

    def send(self, path_file, own=False):
        try:
            printf("Getting server status")
            ftp = self.test_connection()
            if ftp is None:
                printf("Client server down, will try again later.")
                return False
            new = path_file
            path_file = self.compress_file(path_file, own)
            if path_file is None:
                printf("No {0} found".format(new.split("/")[-1]))
                return False
            printf("zipping done :)")
            # print(path_file)
            printf("Login into server ...")
            ftp.login(user=self.username, passwd=self.pwd)
            printf("Login successfully :)")
            printf("Starting {0} tranfer now!".format(path_file.split("/")[-1]))
            response = ftp.storbinary("STOR " + path_file.split("/")
                                      [-1], open(path_file, 'rb'), blocksize=1000)
            ftp.close()
            if response.find("successfully") == -1:
                printf("Failed to transfere files :(")
                return False
            printf("Transfere finished successfully :)")
            printf(response)
            printf("Backing up files now ...")
            backup(path_file, own)
            printf("Back up done :)")
            return True
        except:
            set_reschedule("Out")
            printf("Dial out failed :(")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            return False

    def Out(self, filename=None):
        iridium_on(1)
        router_on(1)
        modem_on(1)
        sleep(60)
        try:
            printf("Starting dial out session")
            files_to_send = ["logs/gps_binex.log", "pictures", "dts", "logs/system.log"]
            if filename != None:
                if isinstance(filename, basestring):
                    printf("Sending requested file {0} ...".format(filename))
                    self.send(filename, own=True)
            else:
                if filename is None:
                    filename = files_to_send
                printf("Start sending  files ...")
                for index, name in enumerate(filename):
                    next_in = "Nothing"
                    if index+1 < len(filename):
                        next_in = filename[index+1]
                        if next_in.find(".log"):
                            next_in = next_in.split("/")[-1]
                    if name.find(".log"):
                        printf("Preparing {0} to be sent. Next in queue {1} ...".format(
                            name.split("/")[-1], next_in))
                    else:
                        printf("Preparing {0} to be sent. Next in queue {1} ...".format(
                            name, next_in))
                    resp = self.send(self.default_path+name)
                    if resp and name.find(".log") == -1:
                        # call("rm  -rf {0}".format(self.default_path+name), shell=True)
                        p = Popen("rm  -rf {0}".format(self.default_path+name),
                                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                        out = p.communicate()
                        # print(out)
                        sleep(2)
                        # print(self.default_path+name)
                        os.mkdir(self.default_path+name)
                    elif resp:
                        call("rm  -rf {0}".format(self.default_path+name), shell=True)
                    else:
                        printf("Unknown error occurred. Dial out exit too soon :(")
                        return
            printf("Dial out session complete! Files tree is cleaned :)")
            welcome()
        except:
            set_reschedule("Out")
            printf("Dial out failed ")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        finally:
            iridium_off(1)
            router_off(1)
            # modem_off(1)

    def In(self, time_out=20):
        try:
            from requests import post
            printf("Started dial in section")
            iridium_on(1)
            router_on(1)
            modem_on(1)
            sleep(10)
            reply = post(self.router_host+self.router_config, auth=self.router_auth)
            print(reply.status_code)
            if reply.status_code != 200:
                printf(
                    "Failed to configure the router ip6600. Exiting now, will try again shortly!")
                set_reschedule("In")
                return

            sleep(2)
            reply = post(self.router_host+self.router_confirm, auth=self.router_auth)
            if reply.status_code != 200:
                printf(
                    "Could not save the dial in conjuration. Exiting now, will try again shortly!")
                set_reschedule("In")
                return
            sleep(60*time_out)
            printf("Dial in section timeout")
        except Exception as err:
            printf("Dial out session failed with {0}".format(err))
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            set_reschedule("In")
        finally:
            iridium_off(1)
            router_off(1)
            # modem_off(1)


class sbd():
    def __init__(self):
        pass

    def send(self, message="Testing"):
        try:
            port = ser('/dev/ttyS1')
            port.baudrate = 9600
            port.open()
            iridium_on(1)
            sbd_on(1)
            sleep(1)
            enable_serial()
            sleep(1)
        except:
            printf('Unable to open port')
        else:
            port.write(message + '\r')
            printf('sent SBD message: {0} {1}'.format(message, '\r'))
            sleep(60)
        finally:
            disable_serial()
            sbd_off(1)
            iridium_off(1)

    #Calling this function will call the rest of the device SBD functions 
    def SBD(self):
        self.solar_SBD()

    def solar_SBD(self):
        #collect dictionary of solar data from other scripts
        solarclass = solar_live()
        solar = solarclass.solar_sbd()

        # Commands send to iridium solar data
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(solar))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Solar)")
            else:
                printf("AT&K0 command did not work to the iridium (Solar)")
        else:
            printf("AT command did not work to the iridium (Solar)")
        
        #If solar message sent successfully, move on and call the vaisala funciton
        if message_sent == True:
            printf("Solar message successfuly sent, moving to iridium Vaisala")
            self.vaisala_SBD()
        else:
            printf("Solar message DID NOT SEND, still moving to iridium Vaisala")
            self.vaisala_SBD()

    def vaisala_SBD(self):
        #collect dictionary of vaisala data from other scripts
        vaisalaclass = Average_Reading()
        vaisala = vaisalaclass.vaisala_sbd()

        # Commands send to iridium vaisala data
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(vaisala))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Vaisala)")
            else:
                printf("AT&K0 command did not work to the iridium (Vaisala)")
        else:
            printf("AT command did not work to the iridium (Vaisala)")
        
        #If vaisala message sent successfully, move on and call the cr funciton
        if message_sent == True:
            printf("Vaisala message successfuly sent, moving to iridium CR")
            self.cr_SBD()
        else:
            printf("Vaisala message DID NOT SEND, still moving to iridium CR")
            self.cr_SBD()

    def cr_SBD(self):
        #collect dictionary of CR data from other scripts
        crclass = cr1000x()
        cr = crclass.cr_sbd()

        # Commands send to iridium CR data
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(cr))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (CR)")
            else:
                printf("AT&K0 command did not work to the iridium (CR)")
        else:
            printf("AT command did not work to the iridium (CR)")
        
        #If CR message sent successfully, move on and call the seabird funciton
        if message_sent == True:
            printf("CR message successfuly sent, moving to iridium seabird")
            self.seabird_SBD()
        else:
            printf("CR message DID NOT SEND, still moving to iridium seabird")
            self.seabird_SBD()  

    def seabird_SBD(self):
        #collect dictionary of seabird data from other scripts
        seabird = seabird_sbd

        # Commands send to iridium seabird data
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(seabird))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (seabird)")
            else:
                printf("AT&K0 command did not work to the iridium (seabird)")
        else:
            printf("AT command did not work to the iridium (seabird)")
        
        #If seabird message sent successfully, move on and call the aquadopp funciton
        if message_sent == True:
            printf("seabird message successfuly sent, moving to iridium aquadopp")
            self.aquadopp_SBD()
        else:
            printf("seabird message DID NOT SEND, still moving to iridium aquadopp")
            self.aquadopp_SBD()  

    def aquadopp_SBD(self):
        #collect dictionary of aquadopp data from other scripts
        aquadopp = aquadopp_sbd

        # Commands send to iridium aquadopp data
        message_sent = False
        sbd_port = ser("/dev/ttyUSB0")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(aquadopp))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (aquadopp)")
            else:
                printf("AT&K0 command did not work to the iridium (aquadopp)")
        else:
            printf("AT command did not work to the iridium (aquadopp)")
        
        #If aquadopp message sent successfully, move on and call the (next device) funciton
        if message_sent == True:
            printf("aquadopp message successfuly sent, moving to iridium (next device)")
            #self.(next device)
        else:
            printf("aquadopp message DID NOT SEND, still moving to iridium (next device)")
            #self.(next device)


    def read(self):
        try:
            port = ser('/dev/ttyS1')
            port.baudrate = 9600
            port.timeout = 60
            port.open()
        except:
            printf('Unable to open port')
            return None
        rev = port.read(port.inWaiting())
        return rev


if __name__ == "__main__":
    sbd()
