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
# modified for KA6 @ Crannell Dr, Boulder, CO 5th May, 2015
# added the setgps script, as low batteries will not have the backed up data RR @ 10th St, 7/15/15
# added the timeout on the sbd checker by RR @ 10th St 8/22/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=150
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
gps_return=9
TPSFILELIST="/mnt/saved_images/tpsfilelist"
#
#####################################
#### get what AMIGOS unit this is ###
station=`cat $ID`
#####################################
#
echo ">>>>> Executing $station, $caller @ `date`" > $PORT
sleep 10
####### check Iridium status ########
sbd_ird_chkr()
{
######## check Iridium status first ########
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
local var i=0
local var loop_count=10
#####################################
while [ $SBD == 1 ] && [ $i != $loop_count ]
do
echo "----- SBD in use, $caller waiting, loop=$i, `date +"%T"` UTC" > $PORT
sleep 21
SBD=`cat $SBD_status`
i=`expr $i + 1`
done
if [ $SBD == 1 ] && [ $i == $loop_count ] ; then
echo "xxxxx SBD TIMEOUT on $caller waiting, `date +"%T"` UTC" > $PORT
exit 0
fi
echo "----- SBD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $SBD_status
i=0
#####################################
while [ $IRD == 1 ] && [ $i != $loop_count ]
do
echo "----- IRD in use, $caller waiting, loop=$i, `date +"%T"` UTC" > $PORT 
sleep 21
IRD=`cat $IRD_status`
i=`expr $i + 1`
done
if [ $IRD == 1 ] && [ $i == $loop_count ] ; then
echo "xxxxx IRD TIMEOUT on $caller waiting, `date +"%T"` UTC" > $PORT
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
#####################################
}
#####################################
sbd_ird_chkr
#####################################
#
echo "----- switching on GRS, wait 50s" > $PORT
/mnt/gpio/grs_ON 
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
#############
# let GRS acquire satellites before getting binary data
/mnt/gps/setgps_grs_ttyS0
echo "----- wait 50s" > $PORT
sleep 50
#############
#
cd /var/tmp
######################
echo "----- running $caller for 40 minutes" > $PORT
/mnt/gps/getgps_tps_SDAC_ttyS0_40mins >& /var/tmp/tps.log
/mnt/gpio/grs_OFF 
######################
cd /mnt/saved_images
#
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
#
TPS=$station"_"$DATE"_"$TIME"_tps"
 
echo "----- Creating $TPS.gz" > $PORT
echo "$TPS.gz" >> $TPSFILELIST
 
cp /var/tmp/tps /mnt/saved_images/$TPS

gzip $TPS
cp /var/tmp/tps.log /mnt/saved_images/$TPS.log
echo "Creating $TPS.gz" >> /mnt/saved_images/$TPS.log
######################
sleep 1
rm /var/tmp/tps
rm /var/tmp/tps.log
#
echo "----- RS232 going off now! " > $PORT
echo "<<<<< $station, $caller exit @ `date`" > $PORT
sleep 1
/mnt/gpio/rs232_OFF
######################
# clear the busy flag
echo "0" > $SBD_status
echo "0" > $IRD_status
######################
#

exit 0
