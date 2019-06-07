#!/bin/sh
#
# 2015/01/24 Ronald Ross @ Crannell, Boulder
# Modified for SDAC and Triton3
# added the timeout on the sbd checker by RR @ 10th St 9/27/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
MAXMSGSIZE=150
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

rm /var/tmp/imm
rm /var/tmp/imm2
rm /var/tmp/sbe*
rm /var/tmp/device*
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
imm_chkr()
{
res=$?
if [ $res == 0 ] ; then
echo "***** all good result for $1, `date +"%T"` UTC" > $PORT
fi
#
if [ $res == 1 ] ; then
echo "!!!!! timeout in getting sync result for $1, `date +"%T"` UTC" > $PORT
echo "!!!!! timeout in getting sync result for $1, `date +"%T"` UTC" >> /mnt/logs/imm_status
echo 1 > /var/tmp/device$2
fi
#
if [ $res == 2 ] ; then
echo "!!!!! timeout in getting data result for $1, `date +"%T"` UTC" > $PORT
echo "!!!!! timeout in getting data result for $1, `date +"%T"` UTC" >> /mnt/logs/imm_status
echo 1 > /var/tmp/device$2
fi
#
if [ $res == 3 ] ; then
echo "!!!!! ERROR in getting data result for $1, `date +"%T"` UTC" > $PORT
echo "!!!!! ERROR in getting data result for $1, `date +"%T"` UTC" >> /mnt/logs/imm_status
echo 1 > /var/tmp/device$2
fi
}
#
#####################################
#
####### check Iridium status ########
sbd_ird_chkr
#####################################
echo "----- switching on IMM" > $PORT
/mnt/gpio/imm_ON
###################################
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
###################################
#
# now get the IMM data
#
/mnt/sbe/rw_IMM_ttyS4a "pwron"
imm_chkr "pwron"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "setenablefullpwrtx=1"
imm_chkr "setenablefullpwrtx=1"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "fcl"
imm_chkr "fcl"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "mls"
imm_chkr "mls"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "t20cc"
imm_chkr "t20cc"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "setenablefullpwrtx=1"
imm_chkr "setenablefullpwrtx=1"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "swt"
imm_chkr "swt"
sleep 5
/mnt/sbe/rw_IMM_ttyS4a "#41outputformat=2"
imm_chkr "#41outputformat=2" "41"
sleep 1
/mnt/sbe/rw_IMM_ttyS4a "#42outputformat=2"
imm_chkr "#42outputformat=2" "42"
sleep 1
######
# get sbe41 status
#/mnt/sbe/rw_IMM_ttyS4a "#41ds"
#sleep 2
######
# tss = take a sample, store in FLASH
# /mnt/sbe/rw_IMM_ttyS4a "#41tss"
/mnt/sbe/rw_IMM_ttyS4a "#41ts"
imm_chkr "#41ts" "41"
sleep 1
# /mnt/sbe/rw_IMM_ttyS4a "#41ts"
# sleep 9
# get last sample
# /mnt/sbe/rw_IMM_ttyS4a "#41sl"
sleep 2
######
# get SBE42 status
#/mnt/sbe/rw_IMM_ttyS4a "#42ds"
#sleep 2
# take a sample, store in FLASH
# /mnt/sbe/rw_IMM_ttyS4a "#42tss"
/mnt/sbe/rw_IMM_ttyS4a "#42ts"
imm_chkr "#42ts" "42"
sleep 1
# /mnt/sbe/rw_IMM_ttyS4a "#42ts"
# sleep 9
# get last sample
# /mnt/sbe/rw_IMM_ttyS4a "#42sl"
sleep 2
####### AQUADOPPS #######
# get last sample from AQD77
/mnt/sbe/rw_IMM_ttyS4a "!77samplegetlast"
imm_chkr "!77samplegetlast" "77"
sleep 2
# get last sample from AQD78
/mnt/sbe/rw_IMM_ttyS4a "!78samplegetlast"
imm_chkr "!78samplegetlast" "78"
sleep 2
#
/mnt/sbe/rw_IMM_ttyS4a "pwroff"
############# 
/mnt/gpio/imm_OFF 
############# 
# y=$(cat /var/tmp/imm)
# echo $station "IMM" $DATE $TIME $y > /var/tmp/imm
# cat /var/tmp/imm > $PORT
# cat /var/tmp/imm >> /var/tmp/immdata
#############
# now send wxt data through SBD mode
#############
echo "----- IMM data capture all done, `date`" > $PORT
#########################
/mnt/sbe/imm_strip.sh
#### temporary
# rm /var/tmp/sbe42*
# rm /var/tmp/acq*
###################################
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
###################################
echo "<<<<< $station, $caller exit, `date`" > $PORT
sleep 1
###################################
# clear the busy flag
echo "0" > $SBD_status
echo "0" > $IRD_status
###################################
/mnt/gpio/rs232_OFF
###################################
#
exit 0

