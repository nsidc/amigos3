

"""
Contains classes for  transport implementations.
"""
import requests
import os
from time import sleep
from requests.auth import HTTPDigestAuth
import datetime
# from xml.etree import ElementTree as et

# class urls():


class device_client():
    pass


class ptz_client():
    def __init__(self):
        self.msg = None
        self.url = 'http://192.168.1.108/onvif/ptz_service'
        self.header = None
        self.unit_degreePan = 0.0027777778*2
        self.unit_degreeTiitl = 0.0055555556*4
        self.path = os.getcwd()
        self.snapShop_url = "http://192.168.1.108/onvifsnapshot/media_service/snapshot?channel=1&subtype=0"

    def __get_service(self, service):
        self.headers = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/{0}".format(service.capitalize()+"Move"),
                        'Content-Type': 'application/soap+xml'}

    def __get_soap(self, file_name, service=None, pan=None, titl=None, zoom=None):
        # if service != None:

        if service != None:
            with open(self.path + self.path[-5] + "soap_{0}".format(service)+"_{0}".format(file_name)+".xml", 'r') as soap:
                self.msg = soap.read()
            pan = pan*self.unit_degreePan
            titl = titl*self.unit_degreeTiitl

            zoom = zoom/100.0

            # self.msg = self.msg.replace("{0}", service)
            self.msg = self.msg.replace("{1}", str(titl))
            self.msg = self.msg.replace("{2}", str(pan))
            self.msg = self.msg.replace("{3}", str(zoom))
            return
        with open(self.path + self.path[-5] + "soap_{0}.xml".format(file_name), 'r') as soap:
            self.msg = soap.read()

    def send(self, action, typeof, pan=None, titl=None, zoom=None):
        if pan == None:
            pan = float(self.getStatus()[0])/self.unit_degreePan
        if titl == None:
            titl = float(self.getStatus()[1])/self.unit_degreeTiitl
        if zoom == None:
            zoom = float(self.getStatus()[2])*10
        self.__get_soap(
            file_name=action, service=typeof.capitalize()+"Move", pan=pan, titl=titl, zoom=zoom)
        self.__get_service(typeof)
        reply = requests.post(self.url, data=self.msg, headers=self.header)
        return reply

    def getStatus(self):
        self.__get_soap('getstatus')
        self.header = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/GetStatus",
                       'Content-Type': 'application/soap+xml'}
        reply = requests.post(self.url, data=self.msg, headers=self.header)
        zoom = reply.text.split('><')[8].split('"')[3]
        pan = reply.text.split('><')[7].split('"')[3]
        titl = reply.text.split('><')[7].split('"')[5]
        print("PAN_Position: {0}\nTITL_Position: {1}\nZOOM_Position: {2}\n".format(
            pan, titl, zoom))
        return pan, titl, zoom

    def snapShot(self):
        dt = str(datetime.datetime.now()).split(" ")
        dt = "_".join(dt)
        username = 'admin'  # The cameras user name
        password = '10iLtxyh'  # the cameras password

        # bypass the username and password authentication
        response = requests.get(
            self.snapShop_url, auth=HTTPDigestAuth(username, password))
        f = open('pic.jpg', 'wb')  # opening

        newname = 'photo_'+dt[0:-7]+'.jpg'  # Write the file to the time stamp
        os.rename('pic.jpg', newname)

        f.write(response.content)
        f.close()


if __name__ == "__main__":
    ptz = ptz_client()
    ptz.send(action='titlup', typeof='absolute', pan=175, titl=0, zoom=40)
    sleep(3)
    ptz.getStatus()
    ptz.snapShot()
