from serial import Serial as ser
from gpio import sbd_off, sbd_on, enable_serial, disable_serial, iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
from time import sleep
from execp import printf
from ftplib import FTP
import os
from shutil import copyfileobj, make_archive
import gzip
from monitor import backup


class dial_in():
    def __init__(self, *args, **kwargs):
        self.username = "amigos3"
        self.pwd = ""
        self.host = ""
        self.default_path = "/media/mmcblk0p1/"

    def test_connection(self):
        pass

    def find_files(self):
        pass

    def send(self):
        pass

    def dialin(self):
        router_off(1)
        modem_on(1)
        sleep(1)
        iridium_on(1)
        sleep(60*20)
        iridium_off(1)
        router_off(1)


class dial():
    def __init__(self, *args, **kwargs):
        self.username = "amigos3"
        self.pwd = "zaehoD1a"
        self.hostname = "128.138.135.165"
        self.default_path = "/media/mmcblk0p1/"

    def test_connection(self):
        response = os.system("ping -c 1 " + self.hostname)
        return response

    def compress_file(self, file_name, own=False):
        if own is True:
            # print(file_name)
            if os.path.isfile(file_name):
                with open(file_name, 'rb') as f_in, gzip.open(file_name + '.gz', 'wb') as f_out:
                    copyfileobj(f_in, f_out)
                return file_name + '.gz'
            root_d = file_name.split("/")
            root_d = "/".join(root_d[:-1])
            print(file_name, root_d)
            return make_archive(file_name, 'zip', file_name)
        elif os.path.isfile(file_name):
            with open(file_name, 'rb') as f_in, gzip.open(file_name + '.gz', 'wb') as f_out:
                copyfileobj(f_in, f_out)
            return file_name + '.gz'
        elif os.path.isdir(file_name):
            return make_archive(file_name, 'zip', file_name)

    def send(self, path_file, own=False):
        path_file = self.compress_file(path_file, own)
        # print(path_file)
        ftp = FTP(self.hostname)
        ftp.login(user=self.username, passwd=self.pwd)
        # response = ftp.storbinary("STOR " + path_file.split("/")
        #   [-1], open(path_file, 'rb'))
        # print(response)
        backup(path_file, own)

    def Out(self, filename):
        files_to_send = ["/logs/gps_binex.log", "pictures", "dts"]
        if filename is None:
            filename = files_to_send
        server = self.test_connection()
        if server:
            printf("Client server down, will try again later.")
        elif filename != None:
            self.send(filename, own=True)
        elif filename.isinstance("str", filename):
            self.send(filename)
        else:
            for index, name in enumerate(filename):
                self.send(self.default_path+name)

    def In():
        pass

    def dialout(self):
        router_on(1)
        sleep(1)
        iridium_on(1)
        sleep(60)
        iridium_off(1)
        router_off(1)

    def dialin(self):
        router_off(1)
        modem_on(1)
        sleep(1)
        iridium_on(1)
        sleep(60*20)
        iridium_off(1)
        router_off(1)


class sbd():
    pass


def send(message="Testing"):
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 9600
        port.open()
        iridium_on(1)
        sbd_on(1)
        sleep(1)
        iridium_off(1)
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


def read():
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
    d = dial()
    r = d.Out("/home/meha/Desktop/test_files")
    if not r:
        print("Host is up")
    else:
        print("Host down")
