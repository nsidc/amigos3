#!/bin/sh

# revised the voltage thresholds and sleep time at RB 9/15/09
# revised for Triton3 @ RB 1/1/13 and removed Vlow condition
# modified to eliminate the 0 voltage reading occurrence, by RR @ 10th St, 7/2/15
# modified to extend short sleep to 3 minutes, by RR @ 10th St, 9/15/15 
# added a status flag to stop 2 of voltage check function becoming active simultaneously after a sleep time RR @ 10th St 7/16/16
# changed the volts low to 11.7V for sleep to kick in by RR @ 10th St 7/24/16
# removed the re-running of "/mnt/gpio/get_volts" as this clashes with get_pcb.sh by Rr @ 10th St 7/28/16

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

# echo " "
# echo "----- Executing $caller for $1 @ `date`" > $PORT
# echo "----- Executing $caller for $1 @ `date`" >> /mnt/logs/voltage

battery_status="/var/tmp/voltage_status"
volts_file="/var/tmp/volts"
status_file="/mnt/logs/repower_hist"
Vchk_status="/var/tmp/VCHK_status"
sleep_short='+0:03'
sleep_long='+0:50'

# these are the voltage thresholds in mVolts since, we need integers to do compares
Volts_High=12500 # ~12.5V
Volts_Low=11500  # ~11.5V
Volts_VLow=10500 # ~10.5V
multiplier=1000

######## check voltage checker status first if voltage_checker is already in process, exit the incoming one ########
# this can occur after a sleep time when a pending check has been suspended then wakes up making 2 voltage checks active at same time
VCHK=`cat $Vchk_status`
if [ $VCHK == 1 ] ; then
exit
fi
echo "1" > $Vchk_status

########
#
############# go get volts and amps now, data will be copied to /var 

BATTERY_LOW=`cat $battery_status`

get_mVolts()
{
# this clashes with get_pcb.sh
# /mnt/gpio/get_volts
Input_voltage=$(cat $volts_file)
# echo "Input voltage = $Input_voltage @ " `date` > $PORT
Input_voltage=$(echo $Input_voltage $multiplier| awk '{ printf("%4d\n", $1*$2) }')
if [ $Input_voltage == 0 ] ; then 
Input_voltage=12.5
fi 
# echo "Input voltage after multiply = $Input_voltage @ " `date` > $PORT
}

# tickle the watchdog before any changes to the mode
# /root/toggle
# wait until scheduled PCB script has finished
sleep 5
get_mVolts
if [ $Input_voltage -lt $Volts_Low ] ; then
# read again to make sure wait 1 second
sleep 1
echo "Battery Voltage 1st check = " $Input_voltage "mVolts @ " `date` > $PORT
get_mVolts
echo "Battery Voltage 2nd check = " $Input_voltage "mVolts @ " `date` > $PORT
fi

if [ $BATTERY_LOW == 0 ] && [ $Input_voltage -lt $Volts_Low ] ; then
echo "1" > $battery_status
echo "Battery Voltage too LOW!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Status = " `cat $battery_status` > $PORT
echo "Battery Voltage too LOW!! " $Input_voltage "mVolts @ " `date`  >> $status_file
echo "Prepare for short sleep" $sleep_short > $PORT
sleep 3
ifconfig eth0 down
/mnt/gpio/eth_phy_OFF
/mnt/gpio/all_off
# /bin/ps >> /mnt/logs/ps
# echo "-----" `date` >> /mnt/logs/ps
/mnt/sleep/sleep.sh $sleep_short &
echo "0" > $Vchk_status
exit

elif [ $BATTERY_LOW == 1 ] && [ $Input_voltage -lt $Volts_High ]  ; then
echo "Battery Voltage STILL too LOW!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Voltage STILL too LOW!! " $Input_voltage "mVolts @ " `date`  >> $status_file
echo "Prepare for long sleep" $sleep_long > $PORT
sleep 3
ifconfig eth0 down
/mnt/gpio/eth_phy_OFF
/mnt/gpio/all_off
# /bin/ps >> /mnt/logs/ps
# echo "-----" `date` >> /mnt/logs/ps
/mnt/sleep/sleep.sh $sleep_long &
echo "0" > $Vchk_status
exit
fi

if [ $Input_voltage -gt $Volts_High ] && [ $BATTERY_LOW == 1 ] ; then
echo "0" > $battery_status
echo "Battery Voltage OK!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Status = " `cat $battery_status` > $PORT
fi
# clear status flag
echo "0" > $Vchk_status