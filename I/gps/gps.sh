#!/bin/sh
#
# 2009/11/22 Terry Haran
# Updated with tg3.sh code to include SBD of position.
#
# 2010/01/28 Terry Haran
# Updated with fix to AMIGOS 5 made in the field at the
# Beta drill site by Ronald Ross. Fix required changing
# incorrect /mnt/gps/getgps_gps_tty1 to correct /mnt/gps/getgps_tty1. 

PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
station=`cat $ID`
MAXMSGSIZE=114
 
######## check battery first ########

battery_status="/var/voltage_status"

BATTERY_LOW=`cat $battery_status`
#####################################

if [ $BATTERY_LOW == 1 ] ; then
echo "Battery Voltage too LOW for GPS!! " $Input_voltage "mVolts @ " `date` > $PORT
else

#####################################
#            BATTERY OK

# allow the schedule checker time to set the Iridium status
sleep 20

######## check Iridium status first ########

IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
#####################################

while [ $SBD == 1 ]
do
echo "SBD in use, waiting " `date` > $PORT
# echo "SBD in use, waiting " `date` > $PORT
sleep 21
SBD=`cat $SBD_status`
done

echo "SBD is now free " `date` > $PORT
# echo "SBD is now free " `date` > $PORT
#####################################
echo "1" > $SBD_status
#####################################

while [ $IRD == 1 ]
do
echo "Iridium in use, waiting " `date` > $PORT
# echo "Iridium in use, waiting " `date` > $PORT
sleep 21
IRD=`cat $IRD_status`
done

echo "Iridium is now free " `date` > $PORT 
# echo "Iridium is now free " `date` > $PORT

#####################################
echo "Testing SBD mode over ttyS2!! `date` " > $PORT
echo "switching on GPS, wait 30s"  > $PORT
/mnt/gpio/gps_ON  ; /mnt/gpio/rs232_ON
sleep 90

##### get rid of old data
rm /var/gps
rm /var/gpsdata
#####

/mnt/gps/getgps_tty1 -u
/mnt/gpio/gps_OFF 
cat /var/gpsdata

############# 
y=$(cat /var/gpsdata)

echo $station "GPS" $DATE $TIME $y > /var/foo
cat /var/foo

#############

echo "Testing SBD mode over ttyS2!! `date` " > $PORT
# `stty -F $PORT2 cs8 9600`
/mnt/gpio/iridium_ON
echo "iridium on" > $PORT
/mnt/gpio/memsic_ON
echo "memsic on" > $PORT

sleep 31
echo "sending sbdwt" > $PORT

byte_count=`wc -c /var/foo | awk '{print $1;}'`
if [ $byte_count -gt $MAXMSGSIZE ]; then
/mnt/csi/sbd_file_send_ascii_long /var/foo
else
/mnt/weather/sbd_file_send_ascii /var/foo
fi

sleep 32
echo "ended SBD mode" > $PORT
/mnt/gpio/memsic_OFF
/mnt/gpio/iridium_OFF
sleep 1
#########################
# clear the busy flag
echo "0" > $SBD_status

/mnt/gpio/wdt_tick
/mnt/gpio/rs232_OFF

fi
