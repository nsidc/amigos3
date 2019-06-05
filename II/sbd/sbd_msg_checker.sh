#!/bin/sh
#
# 2010/01/10 Terry Haran
# Merged with grs.sh code to include checking battery voltage.
# Changed weather file to wxt.
# Added getting date and time.
# Added printing to stdout and to port.
# Added appending to wxtdata file.
# Modified for SDAC and Triton3
# added more flag checking for Wx8 and for adding UV index 7/22/13 @ RB
# increased the SBD message size to 150 according to the A3LA-R spec
# added the bmp085 data to the string, ie temperature then pressure @ RB by RR 14th Oct 2013
# added the timeout on the sbd checker by RR @ 10th St 8/22/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=150
FLAG=0
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
#
#####################################
#### get what AMIGOS unit this is ###
station=`cat $ID`
#####################################
#
echo ">>>>> Executing $station, $caller @ `date`" > $PORT
sleep 10
#####################################
#
##### check SBD/Iridium status ######
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
sbd_ird_chkr
#####################################
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
echo "----- switching on IRD" > $PORT
/mnt/gpio/ird_ON
echo "----- switching on SBD pin" > $PORT
/mnt/gpio/sbd_ON
# wait for Iridium registration
sleep 40
############# 
/mnt/sbd/check_for_sbd_msg.sh
#############
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
#######################
# now check if message to process
if [ -f /var/tmp/sbd2 ] ; then
/mnt/sbd/process_sbd_msg.sh
fi
#########################
cp /var/tmp/sbd /var/tmp/old_sbd
cp /var/tmp/sbd2 /var/tmp/old_sbd2
rm /var/tmp/sbd*
#########################
echo "----- RS232 going off now! " > $PORT
echo "<<<<< $station, $caller exit, `date`" > $PORT
sleep 1
/mnt/gpio/rs232_OFF
#########################
# clear the busy flag
echo "0" > $SBD_status
echo "0" > $IRD_status
#########################

exit 0


