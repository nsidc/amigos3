#!/bin/sh

# 2010/01/18 Terry Haran
# ftp_upload_tps.sh derived from ftp_upload_thumb.sh
#
# 2010/01/20 Terry Haran
# Added timeout.
# Added cd /mnt/saved_images.
#
# 2010/01/21 Terry Haran
# Added use of $? to get return code from ftp.
# Added rm dummy.txt before starting gwet loop.
# Removed wget loop.
# Replace FTP_MINUTES with TARGET_TIME in call to ps_check_tps.
# altered by RR @ RB August 2011 for K-Amigos
# changed station ID to KA1 and KA2 at MZS JAN25th 2012
# altered at Crannel Dr, Boulder May 8th 2015 by RR
# added the setting of the completion flag_tps (for ps_check_tps_tout) by RR @ 10th St, 7/21/15

# ------------------------------
PORT=/dev/ttyS3
HOST='192.249.115.17'
# HOST='192.168.0.47'
# dummy_URL='http://130.94.184.11/dummy' 
dummy_URL='ftp://192.249.115.17/dummy' 
# dummy_URL='ftp://user:user@192.168.0.47/dummy' 
dummy_tries_file='/mnt/sked_tasks/dummy_tries'
dummy_tries=4
dummy_local_file='/var/tmp/dummy'
ID=/root/station
rm $dummy_local_file
TPSFILELIST=/mnt/saved_images/tpsfilelist
FTP_MINUTES=9
WGET_seconds=120
PS_CHECK_TPS_RETURN_FILE=/var/tmp/ps_check_tps_return
timeout=`expr $FTP_MINUTES \* 60 + 60`
#
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
#
tty -s ; status=$?
if [ $status -eq 0 ]  
then 
PORTused='TERMINAL'
else 
PORTused='CRONTAB' 
fi 
#
rm /var/tmp/ps_list
rm /var/tmp/ps_list_tps
#
#####################################
#### get what AMIGOS unit this is ###
station=`cat $ID`
#####################################
#
echo ">>>>> Executing $station, $caller, $PORTused @ `date`" > $PORT
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
echo "xxxxx SBD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/tps_upload_status
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
echo "xxxxx IRD TIMEOUT on $caller waiting, loop=$i, `date`" >> /mnt/logs/tps_upload_status
exit 0
fi
echo "----- IRD is now free for $caller, `date +"%T"` UTC" > $PORT
#####################################
echo "1" > $IRD_status
# the end of sbd_ird_chkr
}
#####################################
# are there files to upload?
#
if [ ! -s $TPSFILELIST ] ; then
echo "----- No list to upload" > $PORT
exit 0
fi
LIST=`cat $TPSFILELIST`
num_files=`wc -l < $TPSFILELIST`
echo "----- There are $num_files files to FTP upload, the list is" > $PORT
echo "$LIST" > $PORT
#####################################
sbd_ird_chkr
#####################################
/mnt/gpio/tps_upload_devices_on
sleep 10
#####################################
#####################################
cd /var/tmp/
touch /var/tmp/$station
#####################################
path=www/htdocs/$station
##
echo "----- webpath=$path" > $PORT
##
if [ -s $dummy_tries_file ] ; then
dummy_tries=`cat $dummy_tries_file`
fi
################### Script to keep trying to wget dummy before FTP begins, dummy must be non-zero
i=1
while [ ! -s $dummy_local_file ] && [ $i -le $dummy_tries ]
do 
/bin/ash /mnt/sked_tasks/ps_check_wget_tout $WGET_seconds &  
echo "----- in the wget loop" > $PORT
wget $dummy_URL -O $dummy_local_file
echo "----- times thru loop $i" > $PORT
i=`expr $i + 1`
done
#####################################
if [ ! -s $dummy_local_file ] ; then
echo "!!!!! unable to wget $dummy in $dummy_tries attempts" > $PORT
echo "!!!!! unable to receive remote dummy file" > $PORT
echo "!!!!! unable to wget after $i attempts, tries = $dummy_tries @ `date`" >> /mnt/logs/tps_upload_status
echo 0 > /var/tmp/wget_completion_flag
/mnt/gpio/tps_upload_devices_off
exit 0
else
echo "***** got wget after $i attempts, tries = $dummy_tries" > $PORT
echo "***** got wget after $i attempts, tries = $dummy_tries @ `date`" >> /mnt/logs/tps_upload_status
echo "***** received remote dummy file ok" > $PORT
fi
#################################
cd /mnt/saved_images
#################################
CURRENT_TIME=`date +%s`
TARGET_TIME=`expr $CURRENT_TIME + 60 \* $FTP_MINUTES`
# 
# start up secondary checker
/bin/ash /mnt/sked_tasks/ps_check_tps_tout $timeout &  
#
while [ -s $TPSFILELIST ] && [ $CURRENT_TIME -lt $TARGET_TIME ]
do
	DELTA=$((TARGET_TIME-CURRENT_TIME))
    echo "----- CURRENT_TIME: $CURRENT_TIME, TARGET_TIME: $TARGET_TIME, DELTA: $DELTA" > $PORT
    # 
    # just for debugging
    ps >> /var/tmp/ps_list
    echo `date` >> /var/tmp/ps_list
    # 
    TPS=`head -1 $TPSFILELIST`
    FTP_COMMAND="ftp"
    FTP_ARGS="-n $HOST"
    #
# echo "here at line 160" > $PORT
	#
    /bin/ash /mnt/sked_tasks/ps_check_tps "$FTP_COMMAND" "$FTP_ARGS" 0
    /bin/ash /mnt/sked_tasks/ps_check_tps "$FTP_COMMAND" "$FTP_ARGS" $TARGET_TIME &
    echo "----- $FTP_COMMAND $FTP_ARGS $TPS" > $PORT
    #
# echo "here at line 167" > $PORT
	#
#################################
path=$station

$FTP_COMMAND $FTP_ARGS <<END_SCRIPT

quote USER $USER
quote PASS $PASSWD
cd $path
passive
binary
put $TPS
quit
END_SCRIPT
#################################
    FTP_RETURN=$?
    echo "----- FTP_RETURN: $FTP_RETURN" > $PORT
    
    if [ ! -s  $PS_CHECK_TPS_RETURN_FILE ] ; then
	echo "----- Waiting for ps_check_tps to return" > $PORT
    fi
    while [ ! -s $PS_CHECK_TPS_RETURN_FILE ]
    do
	sleep 10
    done
    #
# echo "here at line 195" > $PORT
	#
    PS_CHECK_TPS_RETURN=`cat $PS_CHECK_TPS_RETURN_FILE`
    echo "----- PS_CHECK_TPS_RETURN: $PS_CHECK_TPS_RETURN" > $PORT

    if [ $PS_CHECK_TPS_RETURN -eq 0 ] && [ $FTP_RETURN -eq 0 ] ; then
	echo "----- Removing $TPS from $TPSFILELIST" > $PORT
	grep -v $TPS $TPSFILELIST > /var/tmp/foo
	mv /var/tmp/foo $TPSFILELIST
    fi
    CURRENT_TIME=`date +%s`
#
# echo "here at line 210" > $PORT
#
done
#
# echo "here at line 215" > $PORT
#
if [ ! -s $TPSFILELIST ] ; then
    echo "----- no more files to ftp in $FTPFILELIST" > $PORT
fi
#
# echo "here at line 223" > $PORT
#
if [ $CURRENT_TIME -ge $TARGET_TIME ] ; then
    echo "----- ps_check_tps $FTP_MINUTES minute total timeout exceeded" > $PORT
fi
#    
#########################
#
/mnt/gpio/dial_out_devices_off
echo 1 > /var/tmp/ftp_upload_tps_completion_flag
echo "----- executing dial_out_devices_off & clearing status bits" > $PORT
echo "----- $caller completed OK @ " `date` >> /mnt/logs/tps_upload_status
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
