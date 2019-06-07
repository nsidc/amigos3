#!/bin/sh

# added trail of numbers at end to mark last field, RR @ RB 22nd July 2013
# added the bmp085 data to the string, ie temperature then pressure @ RB by RR 14th Oct 2013

PORT3=/dev/ttyS3
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
Vsolarmultiplier=10
Vfinal_dividor=10000
Imultiplier=790
Ifinal_dividor=100

### BMP085 assigns
bmp085_data=/var/tmp/bmp085
bmp085_pressure=/var/tmp/bmp085_press
bmp085_temperature=/var/tmp/bmp085_temp
###

# echo "----- Executing PCB @ " `date` > $PORT3

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

echo $solar_bottom $Vref_10 $Vdividor $Vsolarmultiplier | awk '{ printf("%1.2f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/solar_bottom
echo $solar_top $Vref_10 $Vdividor $Vsolarmultiplier | awk '{ printf("%1.2f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/solar_top
echo $uv $Vref_10 $Vdividor $Vsolarmultiplier | awk '{ printf("%1.2f\n", ((($1*$2)/$3)/$4)) }' > /var/tmp/uv
#
echo $station "PCB" $DATE $TIME $(cat /var/tmp/temperature)" "$(cat /var/tmp/humidity)" "$(cat /var/tmp/volts)" "$(cat /var/tmp/current)" "$(cat /var/tmp/solar_bottom)" "$(cat /var/tmp/solar_top)" "$(cat /var/tmp/uv)" "$(cat $bmp085_temperature)" "$(cat $bmp085_pressure)" A" > /var/tmp/pcb
echo $station "PCB" $DATE $TIME $(cat /var/tmp/temperature)" "$(cat /var/tmp/humidity)" "$(cat /var/tmp/volts)" "$(cat /var/tmp/current)" "$(cat /var/tmp/solar_bottom)" "$(cat /var/tmp/solar_top)" "$(cat /var/tmp/uv)" "$(cat $bmp085_temperature)" "$(cat $bmp085_pressure)" A" >> /var/tmp/pcbdata


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



