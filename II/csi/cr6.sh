#!/bin/sh
#
# 2/6/15 Ronald Ross @ Crannell, Boulder
# Modified for SDAC and Triton3  and DTS
#
# 06/18/2015 Tim White 
# edited awk instruction to grab RM Young & Therm String data 
# ftp is now "getting" from WindTherm.dat on CR6, which after awk instructions, becomes cr6.dat
# moved the time to switch on Iridium from start to after the CR6 data is captured to minimize power consumption RR @ 10th St March 22nd 2016
# moved the position when Ethernet hub is switched on and off to minimize power consumption RR @ 10th St March 22nd 2016
# added the timeout on the sbd checker by RR @ 10th St 8/22/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
HOST='192.168.0.99'
USER='eager'
ID=/root/station
need_eth_file=/var/tmp/NO_ETH
MAXMSGSIZE=150
#
wait_to_acq=70
CR6=/var/tmp/cr6_flag
echo "0" > $CR6
#
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
station=`cat $ID`
FLAG=0
#
#####################################
# get what AMIGOS unit this is
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
echo "xxxxx SBD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/cr6_status
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
echo "xxxxx IRD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/cr6_status
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
#####################################
}
#####################################
#
cr6_eth_chkr()
{
echo "0" > $CR6
local var i=1
local var loop_count=3
CR6_lcl=0
#
while [ $CR6_lcl == 0 ] && [ $i != $loop_count ]
do
echo > /dev/tcp/$HOST/80 && echo "1" > $CR6 || echo "xxxxx $HOST is DOWN, loop=$i, `date +"%T"` UTC" > $PORT
CR6_lcl=`cat $CR6`
i=`expr $i + 1`
sleep 10
done
if [ $CR6_lcl == 0 ] && [ $i == $loop_count ] ; then
get_out "$HOST is DOWN"
else
echo "***** $HOST is UP, loop=$i, `date +"%T"` UTC" > $PORT
echo "***** $HOST is UP, loop=$i, `date +"%T"` UTC" >> /mnt/logs/cr6_status
fi
}
#
#####################################
get_out()
{
/mnt/gpio/cr6_OFF
echo "0" > $SBD_status
echo "0" > $IRD_status
echo "0" > /var/tmp/cr6_upload_completion_flag
/mnt/gpio/ifconfig_eth0_down
echo "xxxxx $station, $caller exit, $1, `date`" > $PORT
echo "xxxxx $station, TIMEOUT $1, loop=$i, `date`" >> /mnt/logs/cr6_status
echo "----- RS232 going off now!" > $PORT
/mnt/gpio/rs232_OFF
exit 0
}
#
#####################################
sbd_ird_chkr
#
#####################################
#
#####################################
echo "----- switching on CR6, wait $wait_to_acq secs for CR6 data " > $PORT
/mnt/gpio/cr6_ON
###################################
echo "----- switching on RS232" > $PORT
/mnt/gpio/rs232_ON 
###################################
sleep $wait_to_acq
#####################################
/mnt/gpio/ifconfig_eth0_up
#####################################
cr6_eth_chkr
#####################################
ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
ascii
prompt off
lcd /var/tmp/
cd usr
get WindTherm.dat

mdelete *.*
quit
END_SCRIPT
FTP_RETURN=$?
    echo "----- FTP_RETURN: $FTP_RETURN"
    echo "----- FTP_RETURN: $FTP_RETURN" > $PORT
 
sleep 5
#################
/mnt/gpio/cr6_OFF
# now put the dummy data
cd /var/tmp
# process foo to get the date of the data

# added fields 11 - 16 for 4 additional thermistors - Tim White 10/10/2016
awk -F"," 'NR == 5 {print $3 " " $4 " " $5 " " $7 " " $8 " " $9 " " $10 " " $11 " " $12 " " $13 " " $14 " " $15 " " $16 " "}' WindTherm.dat > cr6.dat
# 3=CR6 BattV_Avg, 4=WndSpd (m/s), 5=WndDir (Deg), 7=WndSpd_Max (m/s), 8-11=Thermistors(1-4) (deg C)

y=$(cat /var/tmp/cr6.dat)
echo "$station CR6 $DATE $TIME" $y > /var/tmp/dummy_cr6
###
# now send CR6 data through SBD mode
sleep 1
y=$(cat /var/tmp/dummy_cr6)
echo "----- $y" > $PORT
#
cat /var/tmp/dummy_cr6 >> /var/tmp/cr6data
##################
if [ ! -f $need_eth_file ] ; then
echo "----- Ethernet is UP " > $PORT
cp /var/tmp/cr6data /root/workspace/
else
echo "----- Ethernet is DOWN" > $PORT
fi
##################
############################
/mnt/gpio/ifconfig_eth0_down &
############################
#################
echo "----- switching on IRD" > $PORT
/mnt/gpio/ird_ON
sleep 15
echo "----- switching on SBD pin" > $PORT
/mnt/gpio/sbd_ON
#############
echo "----- now sending CR6 data through SBD" > $PORT
/mnt/sbd/sbd_file_send_ascii /var/tmp/dummy_cr6
echo "----- switching off IRD, but wait 15s" > $PORT
sleep 15
#############
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
#####################################
#   
#########################
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
