#!/bin/sh

# this script takes as many images as you like
# modified by RR 8/26/07 at Mona Vale for Wx7

#position1 is looking down the rest position to protect camera from sun
# test for overcoming ro sytstem

# 2009 Nov 10 Terry Haran
# Added saving Sony files 3-6.
# modified for SDAC by RR @ RB 6th Feb 2013 
# renamed to wget_sony.sh
# removed the cd /var/tmp as it seems to have been causing the next script with "wget" to not execute
# cut down images to just 2 for Wx8 2013, RR @ RB 24th July 2013
rm /var/tmp/*.jpg

PORT=/dev/ttyS3
ID=/root/station
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
station=`cat $ID`

#############
if [ $station == 'Wx7' ]  ; then HOST=192.168.0.20 ; PORT=8082 ; fi
if [ $station == 'Wx8' ]  ; then HOST=192.168.0.20 ; PORT=8082 ; fi
if [ $station == 'Wx11' ] ; then HOST=192.168.0.22 ; PORT=8084 ; fi
if [ $station == 'Wx14' ] ; then HOST=192.168.0.20 ; PORT=8082 ; fi
##
######## check Iridium status first ########
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"
#####################################
#
# get what AMIGOS unit this is
SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
station=`cat $ID`
#####################################

echo "----- Executing $caller @ `date`" > $PORT

pos_safe=/mnt/sony/pos_safe
position1=/mnt/sony/pos1
position2=/mnt/sony/pos2
position3=/mnt/sony/pos3
position4=/mnt/sony/pos4

SONYFILE_01=/var/tmp/Sony_01.jpg
SONYFILE_02=/var/tmp/Sony_02.jpg
SONYFILE_03=/var/tmp/Sony_03.jpg
SONYFILE_04=/var/tmp/Sony_04.jpg
SONYFILE_05=/var/tmp/Sony_05.jpg
SONYFILE_06=/var/tmp/Sony_06.jpg
SONYFILE_txt=/var/tmp/scratch

SONYPICTUREURL=http://$HOST:$PORT/oneshotimage.jpg
# PTZ speed to manual
SONYPTZURL_01=http://$HOST:$PORT/command/ptzf.cgi?VISCA=8101062403FF

echo "----- set auto-pan-tilt to off"
wget $SONYPTZURL_01 -O $SONYFILE_txt
echo "----- Trying to move camera safe position"
# $pos_safe
/mnt/sony/home
sleep 10

echo "----- Trying to move camera to pos1" > $PORT
/mnt/sony/pos1
sleep 10
wget $SONYPICTUREURL -O $SONYFILE_01
sleep 1

echo "----- Trying to move camera to pos2" > $PORT
/mnt/sony/pos2
sleep 10
# echo "----- Trying to read picture " 
wget $SONYPICTUREURL -O $SONYFILE_02
sleep 1

# echo "----- Trying to move camera to pos 3" > $PORT
# /mnt/sony/pos3
# sleep 10
# echo "----- Trying to read picture " 
# wget $SONYPICTUREURL -O $SONYFILE_03
# sleep 1

# echo "----- Trying to move camera to pos 4" > $PORT
# /mnt/sony/pos4
# sleep 10
# echo "----- Trying to read picture " 
# wget $SONYPICTUREURL -O $SONYFILE_04
# sleep 1

# echo "----- Trying to move camera pos 5"
# /mnt/sony/pos5
# sleep 10
# echo "----- Trying to read picture " 
# wget $SONYPICTUREURL -O $SONYFILE_05
# sleep 1

# echo "----- Trying to move camera pos 6"
# /mnt/sony/pos6
# sleep 10
# echo "----- Trying to read picture " 
# wget $SONYPICTUREURL -O $SONYFILE_06
# sleep 1

echo "----- Trying to move camera safe position" > $PORT
# $pos_safe
/mnt/sony/pos_safe

rm  /var/tmp/ptzf.cgi*

echo "----- $station, $caller exit @ `date`" > $PORT

exit 0
