#!/bin/sh

PORT3=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`

Vref_10=33
Tdividor=1000
Vdividor=4095
Idividor=4095
Vmultiplier=7987
Vfinal_dividor=10000
Imultiplier=790
Ifinal_dividor=100

echo "----- Executing PCB @ " `date` > $PORT3

#########
cat /sys/class/hwmon/hwmon0/device/temp1_input > /var/tmp/temp1
cat /sys/class/hwmon/hwmon0/device/humidity1_input > /var/tmp/humidity1
# now get volts
echo 4 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/volts_hex
# now get current
echo 5 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/current_hex
#########

temp_format=$(cat /var/tmp/temp1)
humid_format=$(cat /var/tmp/humidity1)

echo $temp_format $Tdividor | awk '{ printf("%2.2f\n", $1/$2) }' > /var/tmp/temperature
echo $humid_format $Tdividor | awk '{ printf("%2.2f\n", $1/$2) }' > /var/tmp/humidity

awk '{print ("0x"$1)+0 } ' /var/tmp/volts_hex > /var/tmp/volts_dec
volts=$(cat /var/tmp/volts_dec)
echo $volts $Vref_10 $Vdividor $Vmultiplier $Vfinal_dividor | awk '{ printf("%2.2f\n", ((($1*$2)/$3)*$4)/$5 )}' > /var/tmp/volts

awk '{print ("0x"$1)+0 } ' /var/tmp/current_hex > /var/tmp/current_dec
current=$(cat /var/tmp/current_dec)

# calculate the current I = (Data x 7.90)/4095
echo $current $Imultiplier $Idividor $Ifinal_dividor | awk '{ printf("%2.3f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/current

echo $station "PCB" $DATE $TIME $(cat /var/tmp/temperature)" "$(cat /var/tmp/humidity)" "$(cat /var/tmp/volts)" "$(cat /var/tmp/current) >> /var/tmp/pcbdata

