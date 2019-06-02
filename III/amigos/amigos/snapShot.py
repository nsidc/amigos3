
# takes photo in the direction camera is placed at the time of running code
from onvif import ONVIFCamera
import os
import requests
from requests.auth import HTTPDigestAuth

import datetime  # To get the current datetime use:


def photo():
    # Set up the camera object using the ONVIF port.
    mycam = ONVIFCamera('192.168.1.108', 80, 'admin',
                        '10iLtxyh', '/home/coovi/Dropbox/Projects/Jane/Amigos/III/amigos/amigos/onvif/wsdl')
    media = mycam.create_media_service()

    allProfiles = media.GetProfiles()
    mainProfile = media.GetProfile({'ProfileToken': allProfiles[0]._token})

    snapshot = media.GetSnapshotUri({'ProfileToken': mainProfile._token})
    print snapshot
#snapShot_url = snapshot.Uri
# url =  snapshot.Uri #making the url downloadable

# To get the current datetime use:

    dt = str(datetime.datetime.now())

    username = 'admin'  # The cameras user name
    password = '10iLtxyh'  # the cameras password

    # bypass the username and password authentication
    response = requests.get(snapshot.Uri, auth=HTTPDigestAuth(username, password))
    f = open('pic.jpg', 'wb')  # opening

    newname = 'file_'+dt+'.jpg'  # Write the file to the time stamp
    os.rename('pic.jpg', newname)

    f.write(response.content)
    f.close()
