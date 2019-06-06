

"""
Contains classes for  transport implementations.
"""
import requests
import os


# class urls():

class device_client():
    pass


class ptz_client():
    def __init__(self, *args, **kwargs):
        self.msg = None
        self.url = 'http://192.168.1.108/onvif/ptz_service'
        self.header = None
        self.unit_degree = 0.0027777778
        self.path = os.getcwd()

    def __get_service(self, service):
        self.headers = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/{0}".format(service.capitalize()+"Move"),
                        'Content-Type': 'application/soap+xml'}

    def __get_soap(self, file, pan=5, titl=5, zoom=0):
        with open(self.path + self.path[-5] + "soap_{0}.xml".format(file), 'r') as soap:
            self.msg = soap.read()

    def send(self, action, typeof, pan=5, titl=5, zoom=0):
        self.__get_soap(action, pan=5, titl=5, zoom=0)
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


if __name__ == "__main__":
    cl = ptz_client()
    cl.send(action='titlup', typeof='relative')
    cl.getStatus()
