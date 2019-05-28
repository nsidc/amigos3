from onvif import ONVIFCamera

# Set up the camera object using the ONVIF port.
mycam = ONVIFCamera('192.168.1.108', 80, 'admin', '10iLtxyh', '/Users/skylaredwards/python-onvif/wsdl')

#access media service
media = mycam.create_media_service()                

# iterate on encoder configurations
for p in media.GetVideoEncoderConfigurations():
    print p.Encoding
    if p.Encoding == "JPEG":
        print 'JPEG Encoder:' + p._token

        # get encoder options    
        options = media.GetVideoEncoderConfigurationOptions({'ConfigurationToken':p._token})
        print  options.JPEG.ResolutionsAvailable

        # get encoder configuration
        cfg = media.GetVideoEncoderConfiguration({'ConfigurationToken':p._token})

        # select the resolution  
        cfg.Resolution = options.JPEG.ResolutionsAvailable[0]

        # update the encoder configuration
        request = media.create_type('SetVideoEncoderConfiguration')
        request.Configuration = cfg
        request.ForcePersistence = True
        media.SetVideoEncoderConfiguration(request)