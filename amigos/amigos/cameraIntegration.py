# The pan movement moves at 100 degrees per second 3.5s =350 degrees

from time import sleep
import time
import pdb
from onvif import ONVIFCamera
import gc

from snapShot import photo  # function written in the same folder called snapShot.py
start_time = time.time()
XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

gc.enable()


def perform_move(ptz, request, timeout):

    # print(ptz.ContinuousMove(request), request)
    # Start continuous move runs through all sequences
    ptz.ContinuousMove(request)
    # print(dir(ptz.ContinuousMove(request)))
    # Wait a certain time to get to certain position
    sleep(timeout)
    # Stop continuous move after the time period runs out or the camera can no longer move in that direction
    ptz.Stop({'ProfileToken': request.ProfileToken})


def move_up(ptz, request, timeout):
    # print ('move up...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


def move_down(ptz, request, timeout):
    # print ('move down...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


def move_right(ptz, request, timeout):
    # print ('move right...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


def move_left(ptz, request, timeout):
    # print ('move left...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


def continuous_move():
    # import pdb
    # pdb.set_trace()
    # IP Address, port, username, password
    mycam = ONVIFCamera('192.168.1.108', 80, 'admin',
                        '10iLtxyh', '/home/coovi/Dropbox/Projects/Jane/Amigos/III/amigos/amigos/onvif/wsdl', no_cache=True)
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()
    # print (dir(ptz))
    # Get target profile
    media_profile = media.GetProfiles()[0]
    # print(media_profile[0])
    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    # print(ptz_configuration_options)
    # print('above line 70')
    request = ptz.create_type('ContinuousMove')
    # print(type(request))
    request.ProfileToken = media_profile._token
    # print('Profil_Token:', request.ProfileToken)
    ptz.Stop({'ProfileToken': media_profile._token})

    # NOTE: X and Y are velocity vector; get range of pan and tilt
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
    # pdb.set_trace()
    # move down initialize as the first starting movement
    move_down(ptz, request, 5)
    sleep(1)  # after moving the camera waits 1 second
    # photo() #taking a photo at the location

    # move right till in next initial position (should be facing tower)
    move_right(ptz, request, 5)

    # move up 45 degrees
    move_up(ptz, request, .5)
    sleep(2)
    # photo()

    # move up
    move_up(ptz, request, .6)
    sleep(2)
    # photo()

    # move left
    move_left(ptz, request, .80)
    sleep(2)
    # photo()

    # move left
    move_left(ptz, request, .70)
    sleep(2)
    # photo()

    # move left
    move_left(ptz, request, .75)
    sleep(2)
    # photo()


if __name__ == '__main__':
    continuous_move()  # calling the function continuous_move()
    # print ("My program took", time.time() - start_time, "to run")
