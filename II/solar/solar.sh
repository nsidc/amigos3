#!/bin/sh


PORT3=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`

echo "----- Executing SOLAR @ " `date` > $PORT3

/mnt/gpio/solar_ON
/mnt/gpio/gpio.sh V5_ENA_ON
/mnt/gpio/gpio.sh V5_SWITCH_ENA_ON
/mnt/gpio/gpio.sh SERIAL_ENA_ON

######## check Iridium status first ########
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
#####################################

while [ $SBD == 1 ]
do
echo "SBD in use, SOLAR waiting " `date` > $PORT3
# echo "SBD in use, waiting " `date` > $PORT3
sleep 21
SBD=`cat $SBD_status`
done

echo "SBD is now free for SOLAR " `date` > $PORT3
# echo "SBD is now free " `date` > $PORT3
#####################################
echo "1" > $SBD_status
#####################################

while [ $IRD == 1 ]
do
echo "Iridium in use, SOLAR waiting " `date` > $PORT3 
# echo "Iridium in use, waiting " `date` > $PORT3
sleep 21
IRD=`cat $IRD_status`
done

echo "Iridium is now free for SOLAR " `date` > $PORT3
# echo "Iridium is now free " `date` > $PORT3
#####################################


#####################################
echo "switching on RS232" > $PORT3
/mnt/gpio/rs232_ON 
echo "switching on IRD" > $PORT3
/mnt/gpio/ird_ON
sleep 15
echo "switching on SBD pin" > $PORT3
/mnt/gpio/sbd_ON
echo "switching on SOLAR SENSORS " > $PORT3
/mnt/gpio/solar_ON
#############
echo 0 > /sys/class/gpio/mcp3208-gpio/index

cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/volts_hex
volts_bottom=$(cat /var/tmp/volts_hex)

echo 1 > /sys/class/gpio/mcp3208-gpio/index

cat /sys/class/gpio/mcp3208-gpio/data > /var/tmp/volts_hex
volts_top=$(cat /var/tmp/volts_hex)

#############
/mnt/gpio/solar_OFF
#############

/usr/bin/perl /mnt/gpio/hex_dec $volts_bottom > /var/tmp/solar_bottom
/usr/bin/perl /mnt/gpio/hex_dec $volts_top > /var/tmp/solar_top

bottom=$(cat /var/tmp/solar_bottom)
top=$(cat /var/tmp/solar_top)

echo $station "SOL" $DATE $TIME $bottom $top > /var/tmp/solar

cat /var/tmp/solar > $PORT3
cat /var/tmp/solar >>/var/tmp/solardata 
# echo "solar_bottom = " $bottom "solar_top = " $top
#############
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/solar
#############
/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
#########################
# clear the busy flag
echo "0" > $SBD_status
#########################
echo "SOLAR all done " > $PORT3
sleep 1
/mnt/gpio/rs232_OFF
exit 0


