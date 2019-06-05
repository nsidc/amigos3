#!/bin/sh
#
# 2010/01/13 Terry Haran
# tps.sh derived from grs.sh.
#
# 2010/01/15 Terry Haran
# First working version.
# Creates timestamped tps file in /mnt/upload_tps
#
# 2010/01/17 Terry Haran
# Changed date stamp from MMDDYY to YYYYMMDD and
# time stamp from HHMMSS to HHMM.
#
# 2010/01/18 Terry Haran
# Added creation of log file.
# Changed moving tps and log files from /mnt/upload_tps
# to copying to /mnt/saved_images.
# Added creating tgz file in /mnt/saved_images.
# Added appending tgz filename to /var/tpsfilelist.
# Added more debug printing.
# Fixed creation of log file.
# Fixed appending name of log file into log file.
# Changed filename to $station_$DATE_TIME_tps.
# Changed 20m in message to 20 minutes.
# Fixed creating tgz file in /mnt/saved_images.
#
# 2010/01/21 Terry Haran
# Added cd /mnt/saved_images.
# Removed /mnt/saved_images/ from filenames in /mnt/grs/tpsfilelist.
#
# 2010/11/17 Terry Haran
# Changed 20 minutes to 40 minutes.
#
# 2010/12/13 Bruce Wallin
# Changed 40 minutes to 20 minutes.

PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2
DATE=`date +%Y%m%d`
TIME=`date +%H%M`
ID=/root/station
MAXMSGSIZE=114
TPSFILELIST="/mnt/grs/tpsfilelist"

######## check battery first ########

battery_status="/var/voltage_status"

BATTERY_LOW=`cat $battery_status`
#####################################

if [ $BATTERY_LOW == 1 ] ; then
echo "Battery Voltage too LOW for GRS!! " $Input_voltage "mVolts @ " `date` > $PORT
exit 1
fi

#####################################
#            BATTERY OK

# get what AMIGOS unit this is
station=`cat $ID`

######## check Topcon status ########

GRS_status="/var/GRS_status"

GRS=`cat $GRS_status`

while [ $GRS == 1 ]
do
echo "Topcon in use, waiting " `date`
echo "Topcon in use, waiting " `date` > $PORT
sleep 21
GRS=`cat $GRS_status`
done

echo "Topcon is now free " `date`
echo "Topcon is now free " `date` > $PORT

#####################################
# set the Topcon busy flag
echo "1" > $GRS_status

echo "switching on GRS, wait 90s"
echo "switching on GRS, wait 90s"  > $PORT
/mnt/gpio/grs_ON  ; /mnt/gpio/rs232_ON
sleep 90

#############

cd /mnt/saved_images
 
echo "running /mnt/grs/gettps_tty1 for 20 minutes"
echo "running /mnt/grs/gettps_tty1 for 20 minutes" > $PORT
/mnt/grs/getgps_tps_tty1 >& /var/tps.log

TPS=$station"_"$DATE"_"$TIME"_tps"
echo "Creating $TPS.tgz"
echo "Creating $TPS.tgz" > $PORT
echo "$TPS.tgz" >> $TPSFILELIST
cp /var/tps $TPS
cp /var/tps.log $TPS.log
echo "Creating $TPS.tgz" >> $TPS.log
tar -czv -f $TPS.tgz $TPS $TPS.log
rm $TPS $TPS.log

#########################
/mnt/gpio/grs_OFF 
# clear the Topcon busy flag
echo "0" > $GRS_status

/mnt/gpio/wdt_tick
/mnt/gpio/rs232_OFF

echo "/mnt/grs/gettps_tty all done "
echo "/mnt/grs/gettps_tty all done " > $PORT
