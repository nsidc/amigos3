#!/bin/sh
sleep 10
NetCamFILE_01=/mnt/upload_images/NC.jpg

NetCamPICTUREURL=http://192.168.0.10:8081/netcam.jpg

echo "Trying to read picture " 
wget $NetCamPICTUREURL -O $NetCamFILE_01
exit 0
