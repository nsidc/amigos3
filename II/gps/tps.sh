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

PORT=/dev/ttyS3

DATE=`date +%Y%m%d`
TIME=`date +%H%M`
ID=/root/station

MAXMSGSIZE=114
TPSFILELIST="/mnt/gps/tpsfilelist"

echo "----- Executing TPS @ " `date` > $PORT

station=`cat $ID`

######## check Topcon status ########
GRS_status="/var/tmp/GRS_status"

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
cd /mnt/saved_images/

echo "running /mnt/grs/getgps_tps_tty0_20mins for 20 minutes"
echo "running /mnt/grs/getgps_tps_20mins for 20 minutes" > $PORT
 
/mnt/gps/getgps_tps_SDAC_ttyS0_20mins >& /var/tmp/tps.log
 
TPS=$station"_"$DATE"_"$TIME"_tps"
 
echo "Creating $TPS.gz"
echo "Creating $TPS.gz" > $PORT
echo "$TPS.gz" >> $TPSFILELIST
 
cp /var/tmp/tps /mnt/saved_images/$TPS

gzip $TPS
cp /var/tmp/tps.log /mnt/saved_images/$TPS.log
echo "Creating $TPS.gz" >> /mnt/saved_images/$TPS.log

# rm /mnt/saved_images/$TPS 
# rm /mnt/saved_images/$TPS.log
#########################
 
/mnt/gpio/grs_OFF 
# clear the Topcon busy flag
 
echo "0" > $GRS_status
/mnt/gpio/rs232_OFF
 
echo "/mnt/grs/getgps_tps_tty0_20mins all done "
echo "/mnt/grs/getgps_tps_tty0_20mins all done " > $PORT
rm /var/tmp/tps
rm /var/tmp/tps.log

exit 0

 
 
