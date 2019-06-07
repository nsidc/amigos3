#!/bin/bash

# 2010 Oct 25 Terry Haran
# Changed /mnt/upload_images to /var/upload_images

# first get real-time images from Sony
# put images in /mnt/upload_images/
# then from the NetCam and put in /mnt/upload_images
# first purge any files not uploaded from revious upload

UPLOAD_IMAGES="/var/upload_images"
rm -fr $UPLOAD_IMAGES
mkdir $UPLOAD_IMAGES

# Take images then turn off camera
/mnt/sked_tasks/ftp_get_sony.sh
/mnt/gpio/sony_OFF

# prompt the dialup and do the upload of thumbnails
/mnt/sked_tasks/ftp_upload_thumb.sh

# Log 
echo --------- FTP upload @ `date` -------- >> /mnt/logs/upload_hist
uptime >> /mnt/logs/upload_hist
