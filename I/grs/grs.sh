#!/bin/sh
#
# 2009/11/22 Terry Haran
# Updated with tg3.sh code to include SBD of position.
# Added -u option in call to getgps_grs_tty1 to update system time.
#
# 2010/01/10 Terry Haran
# Added printing to stdout and to port.
# Added appending to grsdata file.
#
# 2010/01/11 Terry Haran
# Changed grs and grsdata to gps and gpsdata, respectively.
#
# 2010/01/12 Terry Haran
# Added getgps_alt_tty1 for alt and altdata containing altitude data.
#
# 2010/01/14 Terry Haran
# Added checking, setting, and clearing Topcon busy flag GRS_status.

PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=114

######## check battery first ########

battery_status="/var/voltage_status"

BATTERY_LOW=`cat $battery_status`
#####################################

if [ $BATTERY_LOW == 1 ] ; then
echo "Battery Voltage too LOW for GRS!! " $Input_voltage "mVolts @ " `date` > $PORT
else

#####################################
#            BATTERY OK

# allow the schedule checker time to set the Iridium status
sleep 20

# get what AMIGOS unit this is
station=`cat $ID`

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

######## check Topcon status ########

GRS_status="/var/GRS_status"

GRS=`cat $GRS_status`

while [ $GRS == 1 ]
do
echo "Topcon in use, waiting " `date` > $PORT 
# echo "Topcon in use, waiting " `date` > $PORT
sleep 21
GRS=`cat $GRS_status`
done

echo "Topcon is now free " `date` > $PORT
# echo "Topcon is now free " `date` > $PORT

#####################################
# set the Topcon busy flag
echo "1" > $GRS_status

#####################################
echo "switching on GRS, wait 90s"  > $PORT
/mnt/gpio/grs_ON  ; /mnt/gpio/rs232_ON
sleep 90

#############
 
/mnt/grs/getgps_grs_tty1 -u

y=$(cat /var/gps)

echo $station "GRS" $DATE $TIME $y > /var/gps
cat /var/gps
cat /var/gps > $PORT
cat /var/gps >>/var/gpsdata

#############
 
/mnt/grs/getgps_alt_tty1

y=$(cat /var/alt)

echo $station "ALT" $DATE $TIME $y > /var/alt
cat /var/alt
cat /var/alt > $PORT
cat /var/alt >>/var/altdata

#########################
/mnt/gpio/grs_OFF 
# clear the Topcon busy flag
echo "0" > $GRS_status

#############

/mnt/gpio/iridium_ON
echo "iridium on" > $PORT 
/mnt/gpio/memsic_ON
echo "memsic on" > $PORT

sleep 31
echo "sending sbdwt" > $PORT

wc -c /var/gps
byte_count=`wc -c /var/gps | awk '{print $1;}'`
if [ $byte_count -gt $MAXMSGSIZE ]; then
/mnt/csi/sbd_file_send_ascii_long /var/gps
else
/mnt/weather/sbd_file_send_ascii /var/gps
fi

wc -c /var/alt
byte_count=`wc -c /var/alt | awk '{print $1;}'`
if [ $byte_count -gt $MAXMSGSIZE ]; then
/mnt/csi/sbd_file_send_ascii_long /var/alt
else
/mnt/weather/sbd_file_send_ascii /var/alt
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

echo "all done " > $PORT

fi
