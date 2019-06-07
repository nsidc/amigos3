#!/bin/sh
#
PORT=/dev/ttyS0
#
if [ -e /var/down ] ; then
echo "found "done" file from target `date`" > $PORT 
rm /var/down
touch /var/its_there
sleep 30 
echo "switching hub OFF @ `date` " > $PORT 
/mnt/gpio/hub_OFF
sleep 2060
echo "switching hub ON @ `date` " > $PORT 
/mnt/gpio/hub_ON
fi