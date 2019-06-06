

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
        self.url = None
        self.header = None
        self.unit_degree = 0.0027777778
        self.path = os.getcwd()

    def _get_service(self, service):
        headers = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/{0}".format(service.capitalize()+"Move"),
                   'Content-Type': 'application/soap+xml'}
        url = 'http://192.168.1.108/onvif/ptz_service'
        return url, headers

    def _get_soap(self, file):
        with open(self.path + self.path[-5] + "soap_{0}.xml".format(file), 'r') as soap:
            return soap.read()

    def send(self, action=None, typeof=None, pan=5, titl=5, zoom=0):
        self.msg = self._get_soap(action)
        self.url, self.header = self._get_service(typeof)
        reply = requests.post(self.url, data=self.msg, headers=self.header)
        return reply.text

    def getStatus(self):
        self.msg = self._get_soap('getstatus')
        self.header = {'SOAPAction': "http://www.onvif.org/ver20/ptz/wsdl/GetStatus",
                       'Content-Type': 'application/soap+xml'}
        self.url = 'http://192.168.1.108/onvif/ptz_service'
        req = requests.post(self.url, data=self.msg, headers=self.header)
        zoom = req.text.split('><')[8].split('"')[3]
        pan = req.text.split('><')[7].split('"')[3]
        titl = req.text.split('><')[7].split('"')[5]
        print("PAN_Position: {0}\nTITL_Position: {1}\nZOOM_Position: {2}\n".format(
            pan, titl, zoom))
        return pan, titl, zoom


if __name__ == "__main__":
    cl = ptz_client()
    # cl.ptz_send('titlup', 'relative')
    cl.getStatus()
