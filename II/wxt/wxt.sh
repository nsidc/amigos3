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
# added the checking of the reset flag if 1 then set to 0 ie after first WXT SBD by RR @ 10th St 7/24/16 
# added the checking of the sleep flag if 1 then set to 0 ie after first WXT SBD by RR @ 10th St 7/26/16 
# added the timeout on the sbd checker by RR @ 10th St 8/22/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=150
FLAG=0
need_eth_file=/var/tmp/NO_ETH
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
#
#######
rst_flg="/var/tmp/reset_flag"
r_flag=`cat $rst_flg`
#######
slp_flg="/var/tmp/sleep_flag"
s_flag=`cat $slp_flg`
#######
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
echo "xxxxx SBD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/wxt_status
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
echo "xxxxx IRD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/wxt_status
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
#####################################
}
#####################################
#
get_wxt()
{
/mnt/wxt/getweather_tty5
####
if [ $? == 0 ] ; then
{
echo "***** $station, WXT PARSED ok, `date` " > $PORT
echo "***** $station, WXT PARSED ok, `date` " >> /mnt/logs/wxt_status
FLAG=0;
}
else 
echo "!!!!! $station, WXT DID NOT PARSE ok, `date` " > $PORT
echo "!!!!! $station, WXT DID NOT PARSE ok, `date` " >> /mnt/logs/wxt_status
FLAG=`expr $FLAG + 1`
fi
}
#
####### check Iridium status ########
sbd_ird_chkr
#####################################
#
#####################################
echo "----- switching on WXT, wait 45s" > $PORT
/mnt/gpio/wxt_ON 
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
echo "----- switching on IRD" > $PORT
/mnt/gpio/ird_ON
echo "----- switching on SBD pin" > $PORT
/mnt/gpio/sbd_ON
# let WXT520 gather some data and let IRD register
sleep 45
############# 
get_wxt
#############
echo "----- FLAG setting is $FLAG" > $PORT
if [ $FLAG == 1 ] ; then
/mnt/gpio/wxt_OFF
sleep 5
echo "----- Try once more, switching on WXT, wait 45s" > $PORT
/mnt/gpio/wxt_ON
sleep 45
get_wxt
echo "----- FLAG setting is $FLAG" > $PORT
fi
############
/mnt/gpio/wxt_OFF
############# 
y=$(cat /var/tmp/wxt | awk '{ print $1, $2, $3, $4, $5, $6, $7, $8; }')
# incorporate the PCB data into the wxt message
x=$(cat /var/tmp/pcb | awk '{ print $5, $6, $7, $8, $9, $10, $11, $12, $13, $14; }')
echo $station "WXT" $DATE $TIME $y $x > /var/tmp/wxt
cat /var/tmp/wxt >> /var/tmp/wxtdata
#############
#
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/wxt
echo "----- wait additional 10 seconds for SBD bursts" > $PORT
sleep 20
#############
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
############
#
############# check if the station has been reset and flag set to 1 - if reset to 0 
if [ $r_flag == 1 ] ; then
echo "0" > "/var/tmp/reset_flag"
fi
############# check if the station has been in sleep mode and if flag set to 1 - then reset to 0 
if [ $s_flag == 1 ] ; then
echo "0" > "/var/tmp/sleep_flag"
fi
#######
#
echo "----- RS232 going off now! " > $PORT
echo "<<<<< $station, $caller exit @ `date`" > $PORT
sleep 1
/mnt/gpio/rs232_OFF
#########################
# clear the busy flag
echo "0" > $SBD_status
echo "0" > $IRD_status
#########################

exit 0
