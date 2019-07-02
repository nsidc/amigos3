

"""
Contains classes for  transport implementations.
"""
import requests
import os
import subprocess as subprocess
from time import sleep
from requests.auth import HTTPDigestAuth
import datetime
import time
import random
# from xml.etree import ElementTree as et

# class urls():


class device_client():
    pass


class media_client():
    pass


class ptz_client():
    """
    PTZ client for ptz request, take picture, pan, tilt , and zoom.
    """

    def __init__(self):

        self.msg = None
        self.url = 'http://192.168.0.108/onvif/ptz_service'
        self.header = None
        self.unit_degreePan = 0.0027777778*2
        self.unit_degreeTilt = 0.0055555556*4
        self.path = os.getcwd()
        self.snapShop_url = "http://192.168.0.108/onvifsnapshot/media_service/snapshot?channel=1&subtype=0"

    def __get_service(self, service):
        """[summary]

        Arguments:
            service {string} -- can be either relative or relative move to set the type of movement.
        """
        self.headers = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/{0}".format(service.capitalize()+"Move"),
                        'Content-Type': 'application/soap+xml'}  # the headers sent with request, the string format RelativeMove or AbsoluteMove

    def __get_soap(self, service, pan=None, tilt=None, zoom=None):
        """get the soap (xml) file for the request. This the message to be sent

        Arguments:
            move {string} -- the move tosnapSho perform
snapSho
        Keyword Arguments:snapSho
            service {string} -- the typesnapSho of move (default: {None})
            pan {float} -- the angle of snapShopan [-180 to 180 ].  (default: {None})
            tilt {float} -- the tilt possnapShoition [-4 to 45]. (default: {None})
            zoom {float} -- zoom value [-100 to 10]. (default: {None})
        """
        # print(service)

        if service != None and service != 'getstatus':

            with open("/media/mmcblk0p1/amigos/amigos/onvif/soap_{0}.xml".format(service), 'r') as soap:
                self.msg = soap.read()  # open the file
            # calculate the value of the pan  [-1 to 1]
            pan = pan*self.unit_degreePan
            # calculate the value of the tilt [-1 to 1]
            tilt = tilt*self.unit_degreeTilt
            # calculate the value of the soom  [-1 to 1]
            zoom = zoom/100.0

            # format the requested pan.tilt and zoom into the message
            self.msg = self.msg.replace("{1}", str(tilt))
            self.msg = self.msg.replace("{2}", str(pan))
            if service == 'AbsoluteMove':
                self.msg = self.msg.replace("{3}", str(zoom))
                self.msg = self.msg.replace("{4}", str(0))
            elif service == 'RelativeMove':
                self.msg = self.msg.replace("{3}", str(0))
                self.msg = self.msg.replace("{4}", str(zoom))
                print("camera only support zoom in absolute mode")
            # print(zoom)

        # for the function get status
        else:
            # print(self.path)
            with open("/media/mmcblk0p1/amigos/amigos/onvif/soap_{0}.xml".format(service), 'r') as soap:
                self.msg = soap.read()

    def send(self, typeof, pan=None, tilt=None, zoom=None):
        """send the http request to the camera

        Arguments:
            action {string} -- the movement to be made ex: tiltup
            typeof {string} -- the type of movement ex: ablsolute

        Keyword Arguments:
            pan {float} -- the angle of pan [-180 to 180 ].  (default: {None})
            tilt {float} -- the tilt position [-4 to 45]. (default: {None})
            zoom {float} -- zoom value [-100 to 10]. (default: {None})

        Returns:
            [instance] -- return the reply from the server as instance
        """
        # check if the input is not specified used the current value from the camera.
        try:

            if pan == None:
                pan = float(self.getStatus()[0])/self.unit_degreePan
            if tilt == None:
                tilt = float(self.getStatus()[1])/self.unit_degreeTilt
            if zoom == None:
                zoom = float(self.getStatus()[2])*10
            # get the message body to be sent and apply all the value specified

            self.__get_soap(service=typeof.capitalize()+"Move",
                            pan=pan, tilt=tilt, zoom=zoom)

            # get apply the service the the header message
            self.__get_service(typeof)
            # print(self.msg)
            # print('-'*50)
            reply = requests.post(self.url, data=self.msg, headers=self.header)
            # print(reply.text)

            return reply  # return the reply.
        except:
            return None

    def getStatus(self, output=False):
        """Get the starus of the camera

        Returns:
            [floats] -- the current pan, tilt and the zoom
        """
        self.__get_soap('getstatus')  # get the message for status

        self.header = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/GetStatus",
                       'Content-Type': 'application/soap+xml'}  # The header of the status
        reply = requests.post(self.url, data=self.msg,
                              headers=self.header)  # reply is  an xml file
        # get the value of the pan, tilt and zoom from the text
        # print(reply.text)
        zoom = float(reply.text.split('><')[8].split('"')[3])
        pan = float(reply.text.split('><')[7].split(
            '"')[3])
        tilt = float(reply.text.split('><')[7].split(
            '"')[5])
        if output == False:
            return pan, tilt, zoom
        zoom = zoom*100
        pan = pan/self.unit_degreePan
        tilt = tilt/self.unit_degreeTilt
        print("PAN_Position: {0}\nTITL_Position: {1}\nZOOM_Position: {2}\n".format(
            pan, tilt, zoom))

    def snapShot(self):
        try:
            """
            get a snapshot
            """
            dt = str(datetime.datetime.now()).split(" ")
            da = dt[0].split('-')
            da = "".join(da)
            ti = dt[1].split(':')
            ti = "".join(ti)
            dt = da+ti
            username = 'admin'  # The cameras user name
            password = '10iLtxyh'  # the cameras password

            # send the username and password authentication
            response = requests.get(
                self.snapShop_url, auth=HTTPDigestAuth(username, password))
            f = open('/media/mmcblk0p1/amigos/amigos/pic.jpg', 'wb')  # opening

            # Write the file to the time stamp
            newname = '/media/mmcblk0p1/amigos/amigos/'+'photo'+dt[0:-7]+'.jpg'
            # print(dt[0:-7])
            subprocess.call("mv {0} {1}".format(
                '/media/mmcblk0p1/amigos/amigos/pic.jpg', newname), shell=True)
            # os.rename('/media/mmcblk0p1/amigos/amigos/pic.jpg', newname)
            sleep(2)
            f.write(response.content)
            f.close()
            subprocess.call("mv {0} {1}".format(
                newname, "/media/mmcblk0p1/amigos/amigos/picture/"), shell=True)
        except:
            pass

    def cam_test(self):
        self.send(typeof='absolute', pan=random.randint(-180, 180),
                  tilt=random.randint(-45, 45), zoom=random.randint(0, 100))
        sleep(2)
        self.snapShot()
        self.send(typeof='absolute', pan=-100,
                  tilt=0, zoom=random.randint(0, 100))
        sleep(2)
        self.snapShot()
        sleep(1)

        self.send(typeof='absolute', pan=180,
                  tilt=0, zoom=1)
        sleep(2)

        self.snapShot()
        sleep(1)
        self.send(typeof='absolute', pan=random.randint(-180, 180),
                  tilt=random.randint(-45, 45), zoom=1)
        self.snapShot()


# Test the code here
# if __name__ == "__main__":
#     ptz = ptz_client()
#     ptz.send(typeof='relative',
#              pan=25, tilt=0, zoom=0)
#     sleep(2)
#     ptz.snapShot()
#     sleep(1)
#     ptz.getStatus()
#     t1 = time.time()
