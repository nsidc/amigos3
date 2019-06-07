#!/bin/sh

HOUR_NOW=`date +%k`
battery_status="/var/voltage_status"
GRS_status="/var/GRS_status"
IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"

######### check status flags and time ########

BATTERY_LOW=`cat $battery_status`
GRS_BUSY=`cat $GRS_status`
IRD_BUSY=`cat $IRD_status`
SBD_BUSY=`cat $SBD_status`
 
if [[ $BATTERY_LOW == 1 ]] || [[ $GRS_BUSY == 1 ]] ||
   [[ $IRD_BUSY  == 1 ]]   || [[ $SBD_BUSY == 1 ]] ; then
  exit 0
fi
if [[ $HOUR_NOW -ge 2 ]] && [[ $HOUR_NOW -le 11 ]] ; then
  exit 0
fi

###########################

echo 1 > $GRS_status
echo 1 > $IRD_status
echo 1 > $SBD_status

/mnt/gpio/cont_sony_devices_on
sleep 10
/mnt/sked_tasks/cont_get_sony.sh

/mnt/gpio/dial_out_devices_devices_off

echo 0 > $SBD_status
echo 0 > $IRD_status
echo 0 > $GRS_status

