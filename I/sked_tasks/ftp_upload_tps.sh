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
#
PORT=/dev/ttyS0
dummy_tries_file="/mnt/sked_tasks/dummy_tries"
dummy_tries=5
ID=/root/station
TPSFILELIST=/mnt/grs/tpsfilelist
FTP_MINUTES=15
PS_CHECK_TPS_RETURN_FILE=/var/ps_check_tps_return

if [ ! -s $TPSFILELIST ] ; then
    exit 0
fi

######## check battery first ########

battery_status="/var/voltage_status"

BATTERY_LOW=`cat $battery_status`
#####################################

if [ $BATTERY_LOW == 1 ] ; then
    echo "Battery Voltage too LOW for GRS!! " $Input_voltage "mVolts @ " `date` > $PORT
    exit 1
fi

#####################################
#            BATTERY OK

# allow the schedule checker time to set the Iridium status
sleep 20

# get what AMIGOS unit this is
station=`cat $ID`

######## check Iridium status first ########

IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"
GRS_status="/var/GRS_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
GRS=`cat $GRS_status`
#####################################

while [ $SBD == 1 ]
do
    echo "SBD in use, waiting " `date`
    echo "SBD in use, waiting " `date` > $PORT
    sleep 21
    SBD=`cat $SBD_status`
done

echo "SBD is now free " `date`
echo "SBD is now free " `date` > $PORT
#####################################
echo "1" > $SBD_status
#####################################

while [ $IRD == 1 ]
do
    echo "Iridium in use, waiting " `date` 
    echo "Iridium in use, waiting " `date` > $PORT
    sleep 21
    IRD=`cat $IRD_status`
done
    
echo "Iridium is now free " `date`
echo "Iridium is now free " `date` > $PORT
#####################################
echo "1" > $IRD_status
#####################################

######## check Topcon status ########

while [ $GRS == 1 ]
do
    echo "Topcon in use, waiting " `date`
    echo "Topcon in use, waiting " `date` > $PORT
    sleep 21
    GRS=`cat $GRS_status`
done

echo "Topcon is now free " `date`
echo "Topcon is now free " `date` > $PORT
#####################################
echo "1" > $GRS_status
#####################################

/mnt/gpio/ftp_devices_on

# get what AMIGOS unit this is and form account and passwd
station=`cat $ID`

USER=$station

if [ -s $dummy_tries_file ] ; then
    dummy_tries=`cat $dummy_tries_file`
fi

cd /mnt/saved_images

CURRENT_TIME=`date +%s`
TARGET_TIME=`expr $CURRENT_TIME + 60 \* $FTP_MINUTES`

while [ -s $TPSFILELIST ] && [ $CURRENT_TIME -lt $TARGET_TIME ]
do
    echo "CURRENT_TIME: $CURRENT_TIME  TARGET_TIME: _$TARGET_TIME"
    echo "CURRENT_TIME: $CURRENT_TIME  TARGET_TIME: _$TARGET_TIME" > $PORT
    TPS=`head -1 $TPSFILELIST`
    FTP_COMMAND="ftp"
    FTP_ARGS="-n $HOST"

    /mnt/sked_tasks/ps_check_tps "$FTP_COMMAND" "$FTP_ARGS" 0
    /mnt/sked_tasks/ps_check_tps "$FTP_COMMAND" "$FTP_ARGS" $TARGET_TIME &
    echo "$FTP_COMMAND $FTP_ARGS $TPS"
    echo "$FTP_COMMAND $FTP_ARGS $TPS" > $PORT

    $FTP_COMMAND $FTP_ARGS <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd incoming
passive
binary
put $TPS
quit
END_SCRIPT

    FTP_RETURN=$?
    echo "FTP_RETURN: $FTP_RETURN"
    echo "FTP_RETURN: $FTP_RETURN" > $PORT
    
    if [ ! -s  $PS_CHECK_TPS_RETURN_FILE ] ; then
	echo "Waiting for ps_check_tps to return"
    fi
    while [ ! -s $PS_CHECK_TPS_RETURN_FILE ]
    do
	sleep 10
    done

    PS_CHECK_TPS_RETURN=`cat $PS_CHECK_TPS_RETURN_FILE`
    echo "PS_CHECK_TPS_RETURN: $PS_CHECK_TPS_RETURN"
    echo "PS_CHECK_TPS_RETURN: $PS_CHECK_TPS_RETURN" > $PORT

    if [ $PS_CHECK_TPS_RETURN -eq 0 ] && [ $FTP_RETURN -eq 0 ] ; then
	echo "Removing $TPS from $TPSFILELIST"
	echo "Removing $TPS from $TPSFILELIST" > $PORT 
	grep -v $TPS $TPSFILELIST > /var/foo
	mv /var/foo $TPSFILELIST
    fi
    CURRENT_TIME=`date +%s`
done

if [ ! -s $TPSTAPELIST ] ; then
    echo "no more files to ftp in $FTPFILELIST"
    echo "no more files to ftp in $FTPFILELIST" > $PORT
fi
if [ $CURRENT_TIME -ge $TARGET_TIME ] ; then
    echo "ps_check_tps $FTP_MINUTES minute total timeout exceeded" 
    echo "ps_check_tps $FTP_MINUTES minute total timeout exceeded" > $PORT
fi
    
#########################
# clear the busy flags
echo "0" > $GRS_status
echo "0" > $IRD_status
echo "0" > $SBD_status
    
/mnt/gpio/wdt_tick
/mnt/gpio/dial_out_devices_off
    
echo "ftp_upload_tps.sh all done "
echo "ftp_upload_tps.sh all done " > $PORT
    
exit 0
