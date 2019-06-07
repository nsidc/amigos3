#!/bin/sh

# changed to put the SBD/IRD checking in the dial_out_tasks.sh by RR @ 10th St 9/15/16

PORT=/dev/ttyS3
ID=/root/station
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
#
#####################################
# get what AMIGOS unit this is.
station=`cat $ID`
#####################################
echo ">>>>> Executing $station, $caller @ `date`" > $PORT
#####################################
sbd_ird_chkr()
{
######## check Iridium status #######
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
i=0
loop_count=10
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
echo "xxxxx SBD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/dialout_status
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
echo "xxxxx IRD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/dialout_status
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
#####################################
}
#####################################
sbd_ird_chkr
#
#####################################
#
/mnt/gpio/dial_out_devices_on
echo "----- Waiting 120s for Mobo camera to powerup" > $PORT
sleep 120
/mnt/mobo/wget_mobo.sh
# and double check to switch off
#
/mnt/gpio/mobo_OFF
echo "----- Mobo OFF" > $PORT
#
/bin/ash /mnt/sked_tasks/ftp_upload.sh
#
echo "----- FTP UPLOAD done" > $PORT
#
# cleanup files
#
rm /mnt/upload_images/*
rm /var/tmp/*.jpg
rm /var/tmp/dummy
#
echo "***** FTP upload @ `date` ***** >> /mnt/logs/upload_hist 
uptime >> /mnt/logs/upload_hist
#
echo "<<<<< $station, $caller exit @ `date`" > $PORT
#
exit 0
