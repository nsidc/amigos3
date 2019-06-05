#!/bin/sh
set -x
#
# 2010/01/28 Terry Haran
# Increased Preset count from 4 to 5 using code from Ronald Ross.
# Removed scheduled SBD stuff which is not included in AMIGOS.
#
# 2016/07/14 Terry Haran
# Added check that schedule file exists in RAM,
# and copy it to RAM if it doesn't exist, because
# something appears to be deleting if from RAM.

PORT=/dev/ttyS0

dummy='http://192.220.74.204/dummy'
local_dummy='/mnt/dummy'
schedule_file='/var/schedule.dat'
bakup_sked_file="/mnt/sked/schedule.dat"
battery_status="/var/voltage_status"
volts_amps_file="/var/voltage"
test_file="/var/filetest"
IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"
HOUR_NOW=`date +%H`
MINUTE_NOW=`date +%M`
DAY_NOW=`date +%w`
# codes for every day,hour and no day
EVERY_DAY='8'
NEVER='9'
EVERY_HOUR='7'

# remember 0 = Sunday !!!

# make backup of the schedule since this resides in ram
# first check the ram file with flash if differnt then cop ram to flash
# else do nothing
# no longer needed!!!!
# cmp $schedule_file $bakup_sked_file > $test_file
# if [ -s $test_file ] ; then
# fi

# Check that the schedule file exists in RAM,
# and copy it to RAM if it doesn't exist, because
# something appears to be deleting if from RAM.
if [ ! -f $schedule_file ]; then
  cp $bakup_sked_file $schedule_file
fi

######### do a battery status check ###################

BATTERY_LOW=`cat $battery_status`
 
if [ $BATTERY_LOW == 1 ] ; then
exit 0
fi

###########################

DAY_OUT_1=`grep "dial_out_1" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_OUT_1 ] ; then
DAY_OUT_1=${DAY_NOW}
fi
HOUR_ON_OUT_1=`grep "dial_out_1" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_OUT_1=`grep "dial_out_1" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_OUT_1=`grep "dial_out_1" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_OUT_1=`grep "dial_out_1" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `
 
DAY_IN_1=`grep "dial_in_1" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_IN_1 ] ; then
DAY_IN_1=${DAY_NOW}
fi
HOUR_ON_IN_1=`grep "dial_in_1" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_IN_1=`grep "dial_in_1" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_IN_1=`grep "dial_in_1" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_IN_1=`grep "dial_in_1" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

#### test for every hour dial-in scenario
if [ $EVERY_HOUR == $DAY_IN_1 ] ; then
HOUR_ON_IN_1=${HOUR_NOW}
HOUR_OFF_IN_1=${HOUR_NOW}
DAY_IN_1=${DAY_NOW}
# echo "time match for every hour dial-in_1" > $PORT
fi

DAY_OUT_2=`grep "dial_out_2" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_OUT_2 ] ; then
DAY_OUT_2=${DAY_NOW}
fi
HOUR_ON_OUT_2=`grep "dial_out_2" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_OUT_2=`grep "dial_out_2" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_OUT_2=`grep "dial_out_2" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_OUT_2=`grep "dial_out_2" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_IN_2=`grep "dial_in_2" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_IN_2 ] ; then
DAY_IN_2=${DAY_NOW}
fi
HOUR_ON_IN_2=`grep "dial_in_2" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_IN_2=`grep "dial_in_2" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_IN_2=`grep "dial_in_2" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_IN_2=`grep "dial_in_2" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_OUT_3=`grep "dial_out_3" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_OUT_3 ] ; then
DAY_OUT_3=${DAY_NOW}
fi
HOUR_ON_OUT_3=`grep "dial_out_3" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_OUT_3=`grep "dial_out_3" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_OUT_3=`grep "dial_out_3" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_OUT_3=`grep "dial_out_3" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_IN_3=`grep "dial_in_3" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_IN_3 ] ; then
DAY_IN_3=${DAY_NOW}
fi
HOUR_ON_IN_3=`grep "dial_in_3" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_IN_3=`grep "dial_in_3" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_IN_3=`grep "dial_in_3" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_IN_3=`grep "dial_in_3" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_OUT_4=`grep "dial_out_4" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_OUT_4 ] ; then
DAY_OUT_4=${DAY_NOW}
fi
HOUR_ON_OUT_4=`grep "dial_out_4" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_OUT_4=`grep "dial_out_4" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_OUT_4=`grep "dial_out_4" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_OUT_4=`grep "dial_out_4" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_IN_4=`grep "dial_in_4" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_IN_4 ] ; then
DAY_IN_4=${DAY_NOW}
fi
HOUR_ON_IN_4=`grep "dial_in_4" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_IN_4=`grep "dial_in_4" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_IN_4=`grep "dial_in_4" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_IN_4=`grep "dial_in_4" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_OUT_5=`grep "dial_out_5" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_OUT_5 ] ; then
DAY_OUT_5=${DAY_NOW}
fi
HOUR_ON_OUT_5=`grep "dial_out_5" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_OUT_5=`grep "dial_out_5" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_OUT_5=`grep "dial_out_5" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_OUT_5=`grep "dial_out_5" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

DAY_IN_5=`grep "dial_in_5" $schedule_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
if [ $EVERY_DAY == $DAY_IN_5 ] ; then
DAY_IN_5=${DAY_NOW}
fi
HOUR_ON_IN_5=`grep "dial_in_5" $schedule_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
MINUTE_ON_IN_5=`grep "dial_in_5" $schedule_file | awk 'BEGIN { FS=","; } { print $4 ;}' `
HOUR_OFF_IN_5=`grep "dial_in_5" $schedule_file | awk 'BEGIN { FS=","; } { print $5 ;}' `
MINUTE_OFF_IN_5=`grep "dial_in_5" $schedule_file | awk 'BEGIN { FS=","; } { print $6 ;}' `

############# OUT_ON

if [ $HOUR_NOW == $HOUR_ON_OUT_1 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_1 ] && [ $DAY_NOW == $DAY_OUT_1 ] ; then
echo "time match devices_OUT ON 1 @ " `date` > $PORT
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_out_devices_on 
sleep 10
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_2 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_2 ] && [ $DAY_NOW == $DAY_OUT_2 ] ; then
echo "time match devices_OUT ON 2 @ " `date` > $PORT
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_out_devices_on
sleep 10
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_3 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_3 ] && [ $DAY_NOW == $DAY_OUT_3 ] ; then
echo "time match devices_OUT ON 3 @ " `date` > $PORT
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_out_devices_on
sleep 10
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_4 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_4 ] && [ $DAY_NOW == $DAY_OUT_4 ] ; then
echo "time match devices_out ON 4 @ " `date` > $PORT
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_out_devices_on
sleep 10
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_5 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_5 ] && [ $DAY_NOW == $DAY_OUT_5 ] ; then
echo "time match devices_out ON 5 @ " `date` > $PORT
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_out_devices_on
sleep 10
/mnt/sked_tasks/dial_out_tasks.sh &
fi

############# OUT_OFF

if [ $HOUR_NOW == $HOUR_OFF_OUT_1 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_1 ] && [ $DAY_NOW == $DAY_OUT_1 ] ; then
echo "time match devices_OUT OFF 1 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_2 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_2 ] && [ $DAY_NOW == $DAY_OUT_2 ] ; then
echo "time match devices_OUT OFF 2 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_3 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_3 ] && [ $DAY_NOW == $DAY_OUT_3 ] ; then
echo "time match devices_OUT OFF 3 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_4 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_4 ] && [ $DAY_NOW == $DAY_OUT_4 ] ; then
echo "time match devices_OUT OFF 4 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_5 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_5 ] && [ $DAY_NOW == $DAY_OUT_5 ] ; then
echo "time match devices_OUT OFF 5 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_out_devices_off
fi

############### IN_ON

if [ $HOUR_NOW == $HOUR_ON_IN_1 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_1 ] && [ $DAY_NOW == $DAY_IN_1 ] ; then
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_in_devices_on 
sleep 10
echo "time match devices_IN ON 1 @ " `date` > $PORT
fi

if [ $HOUR_NOW == $HOUR_ON_IN_2 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_2 ] && [ $DAY_NOW == $DAY_IN_2 ] ; then
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_in_devices_on 
sleep 10
echo "time match devices_IN ON 2 @ " `date` > $PORT
fi

if [ $HOUR_NOW == $HOUR_ON_IN_3 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_3 ] && [ $DAY_NOW == $DAY_IN_3 ] ; then
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_in_devices_on 
sleep 10
echo "time match devices_IN ON 3 @ " `date` > $PORT
fi

if [ $HOUR_NOW == $HOUR_ON_IN_4 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_4 ] && [ $DAY_NOW == $DAY_IN_4 ] ; then
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_in_devices_on 
sleep 10
echo "time match devices_IN ON 4 @ " `date` > $PORT
fi

if [ $HOUR_NOW == $HOUR_ON_IN_5 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_5 ] && [ $DAY_NOW == $DAY_IN_5 ] ; then
# this sets a lock out to stop SBD operating simultaneously
echo 1 > $IRD_status
/mnt/gpio/dial_in_devices_on 
sleep 10
echo "time match devices_IN ON 5 @ " `date` > $PORT
fi

############# IN_OFF

if [ $HOUR_NOW == $HOUR_OFF_IN_1 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_1 ] && [ $DAY_NOW == $DAY_IN_1 ] ; then
echo "time match devices_IN OFF 1 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_in_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_2 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_2 ] && [ $DAY_NOW == $DAY_IN_2 ] ; then
echo "time match devices_IN OFF 2 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_in_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_3 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_3 ] && [ $DAY_NOW == $DAY_IN_3 ] ; then
echo "time match devices_IN OFF 3 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_in_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_4 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_4 ] && [ $DAY_NOW == $DAY_IN_4 ] ; then
echo "time match devices_IN OFF 4 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_in_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_5 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_5 ] && [ $DAY_NOW == $DAY_IN_5 ] ; then
echo "time match devices_IN OFF 5 @ " `date` > $PORT
# this allows SBD to go ahead and use Iridium 
echo 0 > $IRD_status
/mnt/gpio/dial_in_devices_off
fi
