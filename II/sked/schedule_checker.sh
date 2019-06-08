#!/bin/sh
#
# 2010/01/28 Terry Haran
# Increased Preset count from 4 to 5 using code from Ronald Ross.
# Removed scheduled SBD stuff which is not included in AMIGOS.
# By RR @ RB 9/18/13 - Added ability for every hour dial-out for only preset 1
# changed to impose flag checking now before dial_in_devices_on or dial_out_devices_on by RR @ RB on March 5th 2014
# changed to move the SBD/IRD checking in the dial_out_tasks.sh by RR @ 10th St 9/15/16

PORT=/dev/ttyS3

dummy='http://192.220.74.204/dummy'
local_dummy='/mnt/dummy'
schedule_file='/var/tmp/schedule.dat'
bakup_sked_file="/mnt/sked/schedule.dat"
battery_status="/var/tmp/voltage_status"
volts_amps_file="/var/tmp/voltage"
test_file="/var/tmp/filetest"
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"
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
# echo "----- time match for every hour dial-in_1" > $PORT
fi

#### test for every hour dial-out scenario
if [ $EVERY_HOUR == $DAY_OUT_1 ] ; then
HOUR_ON_OUT_1=${HOUR_NOW}
HOUR_OFF_OUT_1=${HOUR_NOW}
DAY_OUT_1=${DAY_NOW}
# echo "----- time match for every hour dial-out_1" > $PORT
fi
#####################

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

############# OUT_ON

if [ $HOUR_NOW == $HOUR_ON_OUT_1 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_1 ] && [ $DAY_NOW == $DAY_OUT_1 ] ; then
echo "----- time match devices_OUT ON 1 @ " `date` > $PORT
#
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_2 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_2 ] && [ $DAY_NOW == $DAY_OUT_2 ] ; then
echo "----- time match devices_OUT ON 2 @ " `date` > $PORT
#
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_3 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_3 ] && [ $DAY_NOW == $DAY_OUT_3 ] ; then
echo "----- time match devices_OUT ON 3 @ " `date` > $PORT
# 
/mnt/sked_tasks/dial_out_tasks.sh &
fi

if [ $HOUR_NOW == $HOUR_ON_OUT_4 ] && [ $MINUTE_NOW == $MINUTE_ON_OUT_4 ] && [ $DAY_NOW == $DAY_OUT_4 ] ; then
echo "----- time match devices_out ON 4 @ " `date` > $PORT
#
/mnt/sked_tasks/dial_out_tasks.sh &
fi

############# OUT_OFF

if [ $HOUR_NOW == $HOUR_OFF_OUT_1 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_1 ] && [ $DAY_NOW == $DAY_OUT_1 ] ; then
echo "----- time match devices_OUT OFF 1 @ " `date` > $PORT
#
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_2 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_2 ] && [ $DAY_NOW == $DAY_OUT_2 ] ; then
echo "----- time match devices_OUT OFF 2 @ " `date` > $PORT
#
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_3 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_3 ] && [ $DAY_NOW == $DAY_OUT_3 ] ; then
echo "----- time match devices_OUT OFF 3 @ " `date` > $PORT
#
/mnt/gpio/dial_out_devices_off
fi

if [ $HOUR_NOW == $HOUR_OFF_OUT_4 ] && [ $MINUTE_NOW == $MINUTE_OFF_OUT_4 ] && [ $DAY_NOW == $DAY_OUT_4 ] ; then
echo "----- time match devices_OUT OFF 4 @ " `date` > $PORT
#
/mnt/gpio/dial_out_devices_off
fi

############### IN_ON

if [ $HOUR_NOW == $HOUR_ON_IN_1 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_1 ] && [ $DAY_NOW == $DAY_IN_1 ] ; then
echo "----- time match devices_IN ON 1 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_on &
fi

if [ $HOUR_NOW == $HOUR_ON_IN_2 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_2 ] && [ $DAY_NOW == $DAY_IN_2 ] ; then
echo "----- time match devices_IN ON 2 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_on & 
fi

if [ $HOUR_NOW == $HOUR_ON_IN_3 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_3 ] && [ $DAY_NOW == $DAY_IN_3 ] ; then
echo "----- time match devices_IN ON 3 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_on & 
fi

if [ $HOUR_NOW == $HOUR_ON_IN_4 ] && [ $MINUTE_NOW == $MINUTE_ON_IN_4 ] && [ $DAY_NOW == $DAY_IN_4 ] ; then
echo "----- time match devices_IN ON 4 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_on &
fi

############# IN_OFF

if [ $HOUR_NOW == $HOUR_OFF_IN_1 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_1 ] && [ $DAY_NOW == $DAY_IN_1 ] ; then
echo "----- time match devices_IN OFF 1 @ " `date` > $PORT
/mnt/gpio/dial_in_devices_off &
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_2 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_2 ] && [ $DAY_NOW == $DAY_IN_2 ] ; then
echo "----- time match devices_IN OFF 2 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_off &
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_3 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_3 ] && [ $DAY_NOW == $DAY_IN_3 ] ; then
echo "----- time match devices_IN OFF 3 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_off &
fi

if [ $HOUR_NOW == $HOUR_OFF_IN_4 ] && [ $MINUTE_NOW == $MINUTE_OFF_IN_4 ] && [ $DAY_NOW == $DAY_IN_4 ] ; then
echo "----- time match devices_IN OFF 4 @ " `date` > $PORT
#
/mnt/gpio/dial_in_devices_off &
fi
