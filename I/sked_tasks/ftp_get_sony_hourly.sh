#!/bin/sh

# this script takes as many images as you like
# modified by RR 9/18/08 at Rose Bay for Wx8
# modified again to put hourly images in /var instead of CF

#position1 is looking down the rest position to protect camera from sun
cd /var

pos_safe=/mnt/sony/pos_safe
position1=/mnt/sony/pos1
position2=/mnt/sony/pos2

SONYFILE_01=/var/latest1.jpg
SONYFILE_02=/var/latest2.jpg
SONYFILE_txt=/var/scratch

SONYPICTUREURL=http://192.168.0.20:8082/oneshotimage.jpg
# PTZ speed to manual
SONYPTZURL_01=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101062403FF

echo "set auto-pan-tilt to off"
wget $SONYPTZURL_01 -O $SONYFILE_txt
sleep 1
echo "Trying to move camera to pos1"
# $position1
/mnt/sony/pos1
sleep 5
wget $SONYPICTUREURL -O $SONYFILE_01
sleep 1
echo "Trying to move camera pos 2"
# $position2
/mnt/sony/pos2
sleep 5
echo "Trying to read picture " 
wget $SONYPICTUREURL -O $SONYFILE_02
sleep 1
echo "Trying to move camera safe position"
# $pos_safe
/mnt/sony/pos_safe
sleep 2
exit 0
