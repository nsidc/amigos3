#!/bin/sh
#
# 2/6/15 Ronald Ross @ Crannell, Boulder
# Modified for SDAC and Triton3 and DTS
# modified to append date channels, by RR @ 10th St April 16th 2016
# added the copying of cr6, imm and wxt data when the eth link is up as the NO_ETH parameter is in place in /var/tmp by RR @ April 17 2016 @ 10th St
# added the timeout on the sbd checker by RR @ 10th St 8/22/16
# added check for NFS_server exists for transfers

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
#
HOST='192.168.0.66'
NFS_SERVER='192.168.0.47'
USER='dts'
wait_to_acq1=100
wait_to_acq2=300
swoff_wait=60
ps_wait=60
DTS=/var/tmp/dts_flag
NFS_SERVER_flag=/var/tmp/nfs_flag
echo "0" > $NFS_SERVER_flag
echo "0" > $DTS
#
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"
#
FLAG=0
ID=/root/station
bkup='/mnt/saved_images'
TPSFILELIST=/mnt/saved_images/tpsfilelist
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

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
#
dts_eth_chkr()
{
echo "0" > $DTS
local var i=1
local var loop_count=3
DTS_lcl=0
#
while [ $DTS_lcl == 0 ] && [ $i != $loop_count ]
do
echo > /dev/tcp/$HOST/80 && echo "1" > $DTS || echo "xxxxx $HOST is DOWN, loop=$i, `date +"%T"` UTC" > $PORT
DTS_lcl=`cat $DTS`
i=`expr $i + 1`
sleep 10
done
if [ $DTS_lcl == 0 ] && [ $i == $loop_count ] ; then
get_out "$HOST is DOWN"
else
echo "***** $HOST is UP, loop=$i, `date +"%T"` UTC" > $PORT
echo "***** $HOST is UP, loop=$i, `date +"%T"` UTC" >> /mnt/logs/dts_status
fi
}
#
#####################################
get_out()
{
/mnt/gpio/dts_OFF
echo "0" > $SBD_status
echo "0" > $IRD_status
echo "0" > /var/tmp/dts_upload_completion_flag
/mnt/gpio/ifconfig_eth0_down
echo "xxxxx $station, $caller exit, $1, `date`" > $PORT
echo "xxxxx $station, TIMEOUT $1, loop=$i, `date`" >> /mnt/logs/dts_status
echo "----- RS232 going off now!" > $PORT
/mnt/gpio/rs232_OFF
exit 0
}
#
#####################################
#
sbd_ird_chkr
#####################################
/mnt/gpio/dts_ON
echo "----- switching on DTS, wait $wait_to_acq1 secs to test DTS eth" > $PORT
sleep $wait_to_acq1
/mnt/gpio/ifconfig_eth0_up
dts_eth_chkr
echo "----- wait $wait_to_acq2 secs to acquire DTS data" > $PORT
/mnt/gpio/ifconfig_eth0_down &
sleep $wait_to_acq2
###################################
/mnt/gpio/ifconfig_eth0_up
###################################
cd /var/tmp
###################################
echo "----- ps_check_dts now launched for wait time $ps_wait secs" > $PORT
/mnt/dts/ps_check_dts $ps_wait &
###################################

rm /var/tmp/channel*

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
ascii
prompt off
lcd /var/volatile/cache

get channel\ 1.ddf ch1_`date +\%H\%M_\%m\%d\%y`.ddf
get channel\ 2.ddf ch2_`date +\%H\%M_\%m\%d\%y`.ddf
get channel\ 3.ddf ch3_`date +\%H\%M_\%m\%d\%y`.ddf
get channel\ 4.ddf ch4_`date +\%H\%M_\%m\%d\%y`.ddf

mdelete *.*
quit
END_SCRIPT
FTP_RETURN=$?
    echo "----- FTP_RETURN: $FTP_RETURN"
    echo "----- FTP_RETURN: $FTP_RETURN" > $PORT
#
###################################
ssh Administrator@192.168.0.66 './killdts'
ssh Administrator@192.168.0.66 './shutdwn'
sleep 10
ssh Administrator@192.168.0.66 './killdts'
sleep 5
ssh Administrator@192.168.0.66 './killdts'
###################################
echo "----- switching off DTS, but wait $swoff_wait secs for windows server to shutdown" > $PORT
sleep $swoff_wait
###################################
/mnt/gpio/dts_OFF
###################################
# make backups of all channels
# cp ch*.ddf $bkup/
###################################
cd /var/volatile/cache
# ls -alrt /var/cache/ > $PORT
#*****************************
#####################################
# check if NFS server is up or down
#
echo "0" > $NFS_SERVER_flag
echo > /dev/tcp/$NFS_SERVER/80 && echo "1" > $NFS_SERVER_flag || echo "xxxxx $NFS is DOWN,`date +"%T"` UTC" > $PORT
NSF_SERVER_lcl=`cat $NFS_SERVER_flag`
if [ $NSF_SERVER_lcl == 1 ] ; then
echo "***** $NFS_SERVER is UP,`date +"%T"` UTC" > $PORT
cp ch1*.ddf /root/workspace/
cp ch2*.ddf /root/workspace/
cp ch3*.ddf /root/workspace/
cp ch4*.ddf /root/workspace/
cp /var/tmp/immdata /root/workspace/
cp /var/tmp/wxtdata /root/workspace/
cp /var/tmp/cr6data /root/workspace/
fi
#
/mnt/gpio/ifconfig_eth0_down &
###################################
# rename to have station name prependedon filename
for f in * ; do mv "$f" "$station"_"$f" ; done
#
mv * /var/tmp/
cd /var/tmp
#
# cp *_ch1*.ddf latest1.ddf
# cp *_ch2*.ddf latest2.ddf
# cp *_ch3*.ddf latest3.ddf
# cp *_ch4*.ddf latest4.ddf 
#
gzip *_ch*.ddf
#
ls -alrt *.gz | head -4 > last4_ddf
awk '{print $9}' last4_ddf > last4_ddf_files
#
FILE1=`cat last4_ddf_files | awk 'NR==1 {print $1;}'` 
FILE2=`cat last4_ddf_files | awk 'NR==2 {print $1;}'` 
FILE3=`cat last4_ddf_files | awk 'NR==3 {print $1;}'` 
FILE4=`cat last4_ddf_files | awk 'NR==4 {print $1;}'` 
#
FILE_SIZE1=`cat last4_ddf | awk 'NR==1 {print $5;}'`
FILE_SIZE2=`cat last4_ddf | awk 'NR==2 {print $5;}'`
FILE_SIZE3=`cat last4_ddf | awk 'NR==3 {print $5;}'`
FILE_SIZE4=`cat last4_ddf | awk 'NR==4 {print $5;}'`

echo "----- FILE1 = $FILE1, FILE_SIZE = $FILE_SIZE1" > $PORT
echo "----- FILE2 = $FILE2, FILE_SIZE = $FILE_SIZE2" > $PORT
echo "----- FILE3 = $FILE3, FILE_SIZE = $FILE_SIZE3" > $PORT
echo "----- FILE4 = $FILE4, FILE_SIZE = $FILE_SIZE4" > $PORT
HOUR_NOW=`date +%H`

case "$HOUR_NOW" in
	       "00")  echo "------- put $FILE1 in TPSFILELIST for upload" > $PORT
	       		  echo $FILE1 >> $TPSFILELIST
		      ;;
		   "06")  echo "------- put $FILE2 in TPSFILELIST for upload" > $PORT
		          echo $FILE2 >> $TPSFILELIST
		      ;;
		   "12")  echo "------- put $FILE3 in TPSFILELIST for upload" > $PORT
		          echo $FILE3 >> $TPSFILELIST
		      ;;
		   "18")  echo "------- put $FILE4 in TPSFILELIST for upload" > $PORT
		          echo $FILE4 >> $TPSFILELIST
		      ;;
esac
#
mv *_ch*.gz $bkup/
##################################
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
