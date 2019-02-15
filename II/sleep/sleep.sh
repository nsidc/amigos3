#!/bin/sh

PORT3=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

echo " "
echo "----- Executing $caller for $1 @ `date`" > $PORT3
echo "----- Executing $caller for $1 @ `date`" >> /mnt/logs/sleep_status

# set mode to 1 ie 60 minutes
##################
echo 2 > /sys/class/gpio/wdt_ctl/data 
# and toggle before sleeping
/root/toggle_long
sleep 1
/root/toggle_long
##################
echo 0 > /sys/class/gpio/pwr_ctl/index
echo 0 > /sys/class/gpio/pwr_ctl/data

echo 1 > /sys/class/gpio/pwr_ctl/index
echo 0 > /sys/class/gpio/pwr_ctl/data

echo 2 > /sys/class/gpio/pwr_ctl/index
echo 1 > /sys/class/gpio/pwr_ctl/data

echo 1 > /sys/class/gpio/physw/data
echo 0 > /sys/class/gpio/rtsctl/data

sleep 1
echo "1" > /var/tmp/sleep_flag
apmsleep $1
 
/mnt/gpio/rs232_ON 

# set mode to 0 ie 3 minutes
############
echo 0 > /sys/class/gpio/wdt_ctl/data 
# and toggle
/root/toggle
sleep 1
/root/toggle
#############

sleep 1
echo " "
echo "----- AWAKE after SLEEP of $1 @ `date`" > $PORT3
echo "----- AWAKE after $caller of $1 @ `date`" >> /mnt/logs/sleep_status
