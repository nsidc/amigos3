#!/bin/sh
#
# 2/6/15 Ronald Ross @ Crannell, Boulder
# Modified for SDAC and Triton3 and DTS
# modified to append date channels, by RR @ 10th St April 16th 2016
# added the copying of cr6, imm and wxt data when the eth link is up as the NO_ETH parameter is in place in /var/tmp by RR @ April 17 2016 @ 10th St

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
#
HOST='192.168.0.66'
USER='dts'
ID=/root/station
bkup='/mnt/saved_images'
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

echo "" > $PORT
echo "----- Executing $station, $caller, `date`" > $PORT

sleep 5
######## check Iridium status first ########
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"
#
SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
###################################
while [ $SBD == 1 ]
do
echo "----- SBD in use, $caller waiting, `date`" > $PORT
sleep 21
SBD=`cat $SBD_status`
done
echo "----- SBD is now free for $caller, `date`" > $PORT
###################################
echo "1" > $SBD_status
###################################
while [ $IRD == 1 ]
do
echo "----- IRD in use, $caller waiting, `date`" > $PORT 
sleep 21
IRD=`cat $IRD_status`
done
echo "----- IRD is now free for $caller, `date`" > $PORT
###################################
echo "1" > $IRD_status
###################################
wait_to_acq=210
echo "----- switching on DTS, wait $wait_to_acq secs to acquire data" > $PORT
/mnt/gpio/dts_ON
sleep $wait_to_acq
###################################
/mnt/gpio/ifconfig_eth0_up
###################################
cd /var/tmp
###################################
ps_wait=60
echo "----- ps_check_dts now launched for wait time $ps_wait secs" > $PORT
/mnt/dts/ps_check_dts $ps_wait &
###################################

rm /var/tmp/channel*

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
ascii
prompt off
lcd /var/tmp/

get channel\ 1.ddf channel1_`date +\%H\%M_\%m\%d\%y`.ddf
get channel\ 1.dtd channel1_`date +\%H\%M_\%m\%d\%y`.dtd
get channel\ 1.tdf channel1_`date +\%H\%M_\%m\%d\%y`.tdf
get channel\ 3.ddf channel3_`date +\%H\%M_\%m\%d\%y`.ddf
get channel\ 3.dtd channel3_`date +\%H\%M_\%m\%d\%y`.dtd
get channel\ 3.tdf channel3_`date +\%H\%M_\%m\%d\%y`.tdf

mdelete *.*
quit
END_SCRIPT
FTP_RETURN=$?
    echo "----- FTP_RETURN: $FTP_RETURN"
    echo "----- FTP_RETURN: $FTP_RETURN" > $PORT

#
cp channel*.* $bkup/
#
cp channel1*.ddf /root/workspace/
cp channel3*.ddf /root/workspace/
################################### 
# for now while ETH is on - take out later
cp /var/tmp/immdata /root/workspace/
cp /var/tmp/wxtdata /root/workspace/
cp /var/tmp/cr6data /root/workspace/
###################################
###################################
ssh Administrator@192.168.0.66 './killdts'
ssh Administrator@192.168.0.66 './shutdwn'
sleep 10
ssh Administrator@192.168.0.66 './killdts'
sleep 5
ssh Administrator@192.168.0.66 './killdts'
###################################
swoff_wait=60
echo "----- switching off DTS, but wait $swoff_wait secs for windows server to shutdown" > $PORT
sleep $swoff_wait
###################################
/mnt/gpio/dts_OFF
/mnt/gpio/ifconfig_eth0_down &
###################################
echo "----- DTS all done, `date` " > $PORT
mv channel1.ddf latest1.ddf
mv channel3.ddf latest3.ddf 
###################################
echo "----- $station, $caller exit, `date`" > $PORT
sleep 1
###################################
# clear the busy flag
echo "0" > $SBD_status
echo "0" > $IRD_status
###################################
/mnt/gpio/rs232_OFF
###################################
#
rm /var/tmp/*.dtd
rm /var/tmp/*.tdf
mv /var/tmp/channel1*.ddf /var/tmp/ch1.ddf
mv /var/tmp/channel3*.ddf /var/tmp/ch3.ddf
###################################
ch1=ch1.ddf
ch2=ch3.ssf

cd /var/tmp

if [ ! -f $ch1 ] || [ ! -f $ch3 ]; then
# ddf files not gotten
echo "***** $station, No Ch1 or Ch3 found, `date`" > $PORT
echo "***** $station, NO Ch1 or Ch3 found, `date`" >> /mnt/logs/dts
else
echo "----- $station, Yes Ch1 or Ch3 found, `date`" >> /mnt/logs/dts
fi
rm ch*
###################################
exit 0

