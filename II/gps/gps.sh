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
# Modified for SDAC and Triton3 1/18/13 @ RB
# added the timeout on the sbd checker by RR @ 10th St 8/22/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=150
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
FLAG=0
#
#####################################
#### get what AMIGOS unit this is ###
station=`cat $ID`
#####################################
#
echo ">>>>> Executing $station, $caller @ `date`" > $PORT
sleep 10
#####################################
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
echo "xxxxx SBD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/grs_status
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
echo "xxxxx IRD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/gps_status
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
#####################################
}
sbd_ird_chkr
#####################################
echo "----- switching on GRS" > $PORT
/mnt/gpio/grs_ON 
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
echo "----- switching on IRD" > $PORT
/mnt/gpio/ird_ON
echo "----- switching on SBD pin" > $PORT
/mnt/gpio/sbd_ON
# initialize the port and let GRS acquire satellites and let IRD register
/mnt/gps/setgps_grs_ttyS0
echo "----- wait 50s" > $PORT
sleep 50
#############
# update time and date on Triton3
/mnt/gps/getgps_grs_ttyS0 -u
################
if [ $? == 0 ] ; then
{
echo "***** $station, GNRMC PARSED ok, `date` " > $PORT
echo "***** $station, GNRMC PARSED ok, `date` " >> /mnt/logs/gps_status
FLAG=0;
}
else 
{
echo "!!!!! $station, GNRMC DID NOT PARSE ok, `date` " > $PORT
echo "!!!!! $station, GNRMC DID NOT PARSE ok, `date` " >> /mnt/logs/gps_status
FLAG=`expr $FLAG + 1`
}
fi
################
y=$(cat /var/tmp/gps)
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
echo $station "GRS" $DATE $TIME $y > /var/tmp/gps
cat /var/tmp/gps >> /var/tmp/gpsdata
y=$(cat /var/tmp/gps)
sleep 1
#############
# now send GRS data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/gps
echo "----- sending SBD" > $PORT
echo "----- $y" > $PORT
echo "----- wait additional 10 seconds for SBD bursts - RMC" > $PORT
sleep 15
#############
/mnt/gps/getgps_alt_ttyS0
############
if [ $? == 0 ] ; then
{
echo "***** $station, GNGNS PARSED ok, `date` " > $PORT
echo "***** $station, GNGNS PARSED ok, `date` " >> /mnt/logs/gps_status
FLAG=0;
}
else 
{
echo "!!!!! $station, GNGNS DID NOT PARSE ok, `date` " > $PORT
echo "!!!!! $station, GNGNS DID NOT PARSE ok, `date` " >> /mnt/logs/gps_status
FLAG=`expr $FLAG + 1`
}
fi
############
# now switch off the GRS
/mnt/gpio/grs_OFF
#
y=$(cat /var/tmp/altgps)
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
echo $station "GRS" $DATE $TIME $y > /var/tmp/altgps
cat /var/tmp/altgps >> /var/tmp/altgpsdata
y=$(cat /var/tmp/altgps)
sleep 1
#############
# now send GRS data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/altgps
echo "----- sending SBD" > $PORT
echo "----- $y" > $PORT
echo "----- wait additional 10 seconds for SBD bursts - GNS" > $PORT
sleep 15
#############
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
############
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