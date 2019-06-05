

"""
Contains classes for basic HTTP transport implementations.
"""
import requests


# class urls():


class ptz_client():
    def __init__(self, *args, **kwargs):
        self.msg = None
        self.url = None
        self.header = None

    def ptz_service(self, service):
        headers = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/{0}".format(service.capitalize()+"Move"),
                   'Content-Type': 'application/soap+xml'}
        url = 'http://192.168.1.108/onvif/ptz_service'
        return url, headers

    def ptz_read(self, file):

        with open("/home/coovi/pCloudDrive/Projects/Jane/Amigos/III/amigos/amigos/soap/soap_" + "{0}.txt".format(file), 'r') as soap:
            return soap.read()

    def ptz_send(self, action=None, typeof=None):
        self.msg = self.ptz_read(action)
        self.url, self.header = self.ptz_service(typeof)
        req = requests.post(self.url, data=self.msg, headers=self.header)
        # print(req.text)

    def ptz_getStatus(self):
        self.msg = self.ptz_read('getstatus')
        self.header = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/GetStatus",
                       'Content-Type': 'application/soap+xml'}
        self.url = 'http://192.168.1.108/onvif/ptz_service'
        req = requests.post(self.url, data=self.msg, headers=self.header)
        zoom = req.text.split('><')[8].split('"')[3]
        pan = req.text.split('><')[7].split('"')[3]
        titl = req.text.split('><')[7].split('"')[5]
        print("PAN_Position: {0}\nTITL_Position: {1}\nZOOM_Position: {2}\n".format(
            pan, titl, zoom))


if __name__ == "__main__":
    cl = client()
    # cl.ptz_send('titlup', 'relative')
    cl.ptz_getStatus()
