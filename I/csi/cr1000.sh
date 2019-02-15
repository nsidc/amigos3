#!/bin/sh
#
# 2010/01/10 Terry Haran
# Merged with grs.sh code to include checking battery voltage.
# Changed cr1000 data file to csi.
# Added getting date and time.
# Added printing to stdout and to port.
# Added appending to csidata file.

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
echo "Battery Voltage too LOW for CSI!! " $Input_voltage "mVolts @ " `date` > $PORT
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

#####################################
echo "switching on CR1000, don't wait "  > $PORT
/mnt/gpio/cr1000_ON  ; /mnt/gpio/rs232_ON

/mnt/csi/getCR1000_tty2 > /var/csi
/mnt/gpio/cr1000_OFF 

############# 
y=$(cat /var/csi)

echo $station "CSI" $DATE $TIME $y > /var/foo
cat /var/foo
cat /var/foo > $PORT
cat /var/foo >>/var/csidata

#############

# echo "Testing SBD mode over ttyS2!! `date` " > $PORT
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

echo "all done " > $PORT

fi
