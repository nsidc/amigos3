#!/bin/sh
# revised the voltage thresholds and sleep time at RB 9/15/09

PORT=/dev/ttyS0

battery_status="/var/voltage_status"
volts_amps_file="/var/voltage"
status_file="/mnt/logs/repower_hist"
sleep_long='+23hours'
sleep_short='+2min'
first_check=0
second_check=0

# these are the voltage thresholds in mVolts since, we need integers to do compares
Volts_High='12300'
Volts_Low='11500'
Volts_VLow='9500'

############# go get volts and amps now, data will be copied to /var 

BATTERY_LOW=`cat $battery_status`

get_mVolts()
{
/mnt/i2c/i2c_io > /dev/null
Input_voltage=`cat $volts_amps_file | awk 'BEGIN { FS=" "; } { print $3 ;}'`
# echo "input voltage = " $Input_voltage 
# now multiply it to by 1000 to get an integer
Input_voltage=`echo $Input_voltage | awk 'BEGIN { FS=" "; } { print ($1 * 1000) ; }'`
# echo "input voltage after multiply = " $Input_voltage 
}

get_mVolts
if [ $Input_voltage -lt $Volts_Low ] && [ $Input_voltage -gt $Volts_VLow ] ; then
# read again to make sure wait 1 second
sleep 1
echo "Battery Voltage 1st check = " $Input_voltage "mVolts @ " `date` > $PORT
get_mVolts
echo "Battery Voltage 2nd check = " $Input_voltage "mVolts @ " `date` > $PORT
fi

# echo "Battery Status  = " `cat $battery_status` > $PORT
# echo "Battery Voltage 1st check = " $Input_voltage "mVolts @ " `date` > $PORT

if [ $BATTERY_LOW == 1 ] && [ $Input_voltage -lt $Volts_High ] && [ $Input_voltage -gt $Volts_VLow ] ; then
echo "Battery Voltage STILL too LOW!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Voltage STILL too LOW!! " $Input_voltage "mVolts @ " `date`  >> $status_file

echo "Go back to sleep again" > $PORT
/mnt/gpio/all_off
/mnt/gpio/wdt_1day_on
/mnt/gpio/wdt_tick
# just to make sure
/mnt/gpio/wdt_tick
/usr/local/bin/pm_sleep $sleep_long
/mnt/gpio/wdt_1day_off
/mnt/gpio/wdt_tick

elif [ $Input_voltage -lt $Volts_Low ] && [ $Input_voltage -gt $Volts_VLow ] ; then
echo "1" > $battery_status
echo "Battery Voltage too LOW!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Status = " `cat $battery_status` > $PORT
echo "Prepare for sleep" > $PORT
echo "Battery Voltage too LOW!! " $Input_voltage "mVolts @ " `date`  >> $status_file
ifconfig eth0 down
/mnt/gpio/all_off
sleep 1
/mnt/gpio/wdt_1day_off
/mnt/gpio/wdt_tick
# just to make sure
/mnt/gpio/wdt_tick
/usr/local/bin/pm_sleep $sleep_short
/mnt/gpio/wdt_1day_off
/mnt/gpio/wdt_tick
fi

if [ $Input_voltage -gt $Volts_High ] && [ $BATTERY_LOW == 1 ] ; then
echo "0" > $battery_status
echo "Battery Voltage OK!! " $Input_voltage "mVolts @ " `date` > $PORT
echo "Battery Status = " `cat $battery_status` > $PORT
# /mnt/gpio/hub_ON
# sleep 5
# ifconfig eth0 up
# route add default gw 192.168.0.1
fi
