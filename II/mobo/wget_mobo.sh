#!/bin/sh

# this script implements the functions of wget_mobo BUT ignores SBD and IRD flags
# June 19 2015 - Tim White

cd /var/tmp/
PORT=/dev/ttyS3
host=192.168.0.20:8082
ID=/root/station
IMGS="/mnt/saved_images"
volatile="/var/tmp"
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
user=eager
pwd=eager2

cd /var/tmp/
IMGS="/mnt/saved_images"
volatile="/var/tmp/"
rm *.jpg
#
#####################################
#### get what AMIGOS unit this is ###
station=`cat $ID`
#####################################
#
echo ">>>>> Executing $station, $caller @ `date`" > $PORT
#
#####################################
echo "----- getting images left and right, `date`" > $PORT
#
wget "http://$user:$pwd@$host/cgi-bin/image.jpg?camera=left&size=320x240&quality=60" -O mobo_left.jpg;
wget "http://$user:$pwd@$host/cgi-bin/image.jpg?camera=right&size=320x240&quality=60" -O mobo_right.jpg;
#
/mnt/gpio/mobo_OFF
#
echo "----- Mobo OFF" > $PORT
sleep 1
echo "<<<<< $station, $caller exit @ `date`" > $PORT
sleep 1
#
