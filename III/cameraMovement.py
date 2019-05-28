from time import sleep

from onvif import ONVIFCamera

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

def perform_move(ptz, request, timeout):
    # Start continuous move runs through all sequences
    ptz.ContinuousMove(request)
    # Wait a certain time to get to certain position
    sleep(timeout)
    # Stop continuous move after the time period runs out or the camera can no longer move in that direction
    ptz.Stop({'ProfileToken': request.ProfileToken})

def move_up(ptz, request, timeout):
    print 'move up...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)

def move_down(ptz, request, timeout):
    print 'move down...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)

def move_right(ptz, request, timeout):
    print 'move right...'
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def move_left(ptz, request, timeout):
    print 'move left...'
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def continuous_move():
    mycam = ONVIFCamera('192.168.1.108', 80, 'admin', '10iLtxyh', '/Users/skylaredwards/python-onvif/wsdl') #IP Address, port, username, password
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()
    #print ptz
    # Get target profile
    media_profile = media.GetProfiles()[0];

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile._token

    ptz.Stop({'ProfileToken': media_profile._token})

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    #print XMAX, YMAX, YMIN, XMIN


    # move right
    move_right(ptz, request, 0)

    # move left
    move_left(ptz, request, 3.5)

    # Move up
    move_up(ptz, request,0)

    # move down
    move_down(ptz, request,0)

if __name__ == '__main__':
    continuous_move() #calling the function continuous_move()
