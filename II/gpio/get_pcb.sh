#!/bin/sh

# added trail of numbers at end to mark last field, RR @ RB 22nd July 2013
# added the bmp085 data to the string, ie temperature then pressure @ RB by RR 14th Oct 2013
# added variables to report summer or winter and if a reset just occurred by RR at 10th St 7/24/16 - first to Wx11
# added the checking of the sleep flag if 1 then set to 100 otherwise reset to 0 by RR @ 10th St 7/26/16 

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`

Vref_10=33
Tdividor=1000
Vdividor=4095
Idividor=4095
# Vmult was 7987
Vmultiplier=7980
# solar muliplier was 10 made 4 for experiment
# Vsolarmultiplier=4.953
Vsolarmultiplier=10
Vsolarmultiplier_bot=1000
Vsolar_dividor_bot=114
Vfinal_dividor=10000
Imultiplier=790
Ifinal_dividor=100
solar_cal_file="/mnt/solar/solar_cal_file"
#######
rst_flg="/var/tmp/reset_flag"
r_flag=`cat $rst_flg`
#######
slp_flg="/var/tmp/sleep_flag"
s_flag=`cat $slp_flg`
#######
aws_stat="/var/tmp/aws_mode"
aws_status=`cat $aws_stat`
#######
summer_or_winter_flag="0"
#######
if [ -f /mnt/SUMMER ] ; then
summer_or_winter_flag="0"
fi 
#
if [ -f /mnt/WINTER ] ; then
summer_or_winter_flag="10"
fi
######
sleeps="0"
#######
if [ $s_flag == 1 ] ; then
sleeps="100"
fi
#
if [ $s_flag == 0 ] ; then
sleeps="0"
fi
#######
status_char=`expr $summer_or_winter_flag + $r_flag + $aws_status + $sleeps` ;
# echo "sum_win_flg=$summer_or_winter_flag, r_flag=$r_flag, aws_status=$aws_status, sleeps=$sleeps, status char=$status_char" > $PORT
#######
#
### BMP085 assigns
bmp085_data=/var/tmp/bmp085
bmp085_pressure=/var/tmp/bmp085_press
bmp085_temperature=/var/tmp/bmp085_temp
###
#####
if [ -f $solar_cal_file ]; then
#####
# echo "reading solar cal file exists" > $PORT
# echo "reading solar cal file exists"
Vsolar_dividor_bot=`grep "solar_bottom" $solar_cal_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
Vsolarmultiplier_bot=`grep "solar_bottom" $solar_cal_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
Vsolar_dividor_top=`grep "solar_top" $solar_cal_file | awk 'BEGIN { FS=","; } { print $2 ;}' `
Vsolarmultiplier_top=`grep "solar_top" $solar_cal_file | awk 'BEGIN { FS=","; } { print $3 ;}' `
# echo "Vsolar_dividor_bot = $Vsolar_dividor_bot, Vsolarmultiplier_bot = $Vsolarmultiplier_bot" > $PORT
# sleep 2
# echo "Vsolar_dividor_top = $Vsolar_dividor_top, Vsolarmultiplier_top = $Vsolarmultiplier_top" > $PORT
# sleep 2
fi
#####

# echo "----- Executing PCB @ " `date` > $PORT

/mnt/gpio/gpio.sh V5_ENA_ON
/mnt/gpio/gpio.sh V5_SWITCH_ENA_ON
# /mnt/gpio/gpio.sh SERIAL_ENA_ON

#########
# now get temperature and humidity
cat /sys/class/hwmon/hwmon0/device/temp1_input > /var/tmp/temperature
cat /sys/class/hwmon/hwmon0/device/humidity1_input > /var/tmp/humidity
# now get volts
echo 4 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/volts_hex
# now get current
echo 5 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/current_hex
# now get solar
sleep 1
/mnt/gpio/solar_ON
echo 0 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/solar_bottom_hex
#
echo 1 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/solar_top_hex

echo 3 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/uv_hex

/mnt/bmp085/bmp085_press_temp > $bmp085_data

awk ' $1 == "pressure:" {printf "%4.1f\n", $2} ' $bmp085_data > $bmp085_pressure 
awk ' $1 == "temperature:" {printf "%3.1f\n", $2} ' $bmp085_data > $bmp085_temperature 

/mnt/gpio/solar_OFF
#########

temp_format=$(cat /var/tmp/temperature)
humid_format=$(cat /var/tmp/humidity)

echo $temp_format $Tdividor | awk '{ printf("%2.2f\n", $1/$2) }' > /var/tmp/temperature
echo $humid_format $Tdividor | awk '{ printf("%2.2f\n", $1/$2) }' > /var/tmp/humidity

awk '{print ("0x"$1)+0 } ' /var/tmp/volts_hex > /var/tmp/volts_dec
volts=$(cat /var/tmp/volts_dec)
echo $volts $Vref_10 $Vdividor $Vmultiplier $Vfinal_dividor | awk '{ printf("%2.2f\n", ((($1*$2)/$3)*$4)/$5 )}' > /var/tmp/volts

awk '{print ("0x"$1)+0 } ' /var/tmp/current_hex > /var/tmp/current_dec
current=$(cat /var/tmp/current_dec)

# calculate the current I = (Data x 7.90)/4095
echo $current $Imultiplier $Idividor $Ifinal_dividor | awk '{ printf("%2.3f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/current
#
awk '{print ("0x"$1)+0 } ' /var/tmp/solar_bottom_hex > /var/tmp/solar_bottom_dec
awk '{print ("0x"$1)+0 } ' /var/tmp/solar_top_hex > /var/tmp/solar_top_dec
awk '{print ("0x"$1)+0 } ' /var/tmp/uv_hex > /var/tmp/uv_dec
solar_bottom=$(cat /var/tmp/solar_bottom_dec)
solar_top=$(cat /var/tmp/solar_top_dec)
uv=$(cat /var/tmp/uv_dec)

echo $solar_bottom $Vref_10 $Vdividor $Vsolarmultiplier_bot $Vsolar_dividor_bot | awk '{ printf("%1.2f\n", (((($1*$2)/$3)/$4))*$5) }' > /var/tmp/solar_bottom
echo $solar_top $Vref_10 $Vdividor $Vsolarmultiplier | awk '{ printf("%1.2f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/solar_top
echo $uv $Vref_10 $Vdividor $Vsolarmultiplier | awk '{ printf("%1.2f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/uv
#
echo $station "PCB" $DATE $TIME $(cat /var/tmp/temperature)" "$(cat /var/tmp/humidity)" "$(cat /var/tmp/volts)" "$(cat /var/tmp/current)" "$(cat /var/tmp/solar_bottom)" "$(cat /var/tmp/solar_top)" "$(cat /var/tmp/uv)" "$(cat $bmp085_temperature)" "$(cat $bmp085_pressure)" $status_char" > /var/tmp/pcb
echo $station "PCB" $DATE $TIME $(cat /var/tmp/temperature)" "$(cat /var/tmp/humidity)" "$(cat /var/tmp/volts)" "$(cat /var/tmp/current)" "$(cat /var/tmp/solar_bottom)" "$(cat /var/tmp/solar_top)" "$(cat /var/tmp/uv)" "$(cat $bmp085_temperature)" "$(cat $bmp085_pressure)" $status_char" >> /var/tmp/pcbdata


rm /var/tmp/volts_dec
rm /var/tmp/volts_hex
rm /var/tmp/current_dec
rm /var/tmp/current_hex
rm /var/tmp/solar_bottom_dec
rm /var/tmp/solar_top_dec
rm /var/tmp/solar_bottom_hex
rm /var/tmp/solar_top_hex
rm /var/tmp/uv_hex
rm /var/tmp/uv_dec

# added at JBS to reduce current consumption 12/8/15

/mnt/gpio/gpio.sh V5_ENA_OFF
/mnt/gpio/gpio.sh V5_SWITCH_ENA_OFF

