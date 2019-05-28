#takes photo in the direction camera is placed at the time of running code
from onvif import ONVIFCamera
# Set up the camera object using the ONVIF port.
mycam = ONVIFCamera('192.168.1.108', 80, 'admin', '10iLtxyh', '/Users/skylaredwards/python-onvif/wsdl')
media = mycam.create_media_service()                

allProfiles = media.GetProfiles()
mainProfile = media.GetProfile({'ProfileToken' : allProfiles[0]._token})

snapshot = media.GetSnapshotUri({'ProfileToken' : mainProfile._token})
print snapshot
#snapShot_url = snapshot.Uri
#url =  snapshot.Uri #making the url downloadable

#import datetime #Return the date and current time of the Photo being taken 
#now = datetime.datetime.now()
#print 'Current date and time :'
#timeStamp = now.strftime('%Y-%m-%d %H:%M:%S') #Current date and time this should mstch up with the time stamp on the photo
#print timeStamp #variable named timeStamp will display the current time and date 


#To get the current datetime use:

import datetime
dt = str(datetime.datetime.now())

import requests
from requests.auth import HTTPDigestAuth


username = 'admin'
password = '10iLtxyh'

response = requests.get(snapshot.Uri, auth=HTTPDigestAuth(username, password))
f = open('pic.jpg', 'wb') 

import os
newname = 'file_'+dt+'.jpg'
os.rename('pic.jpg', newname)

f.write(response.content)
f.close()


