#!/bin/sh

# Modified for SDAC and Triton3


PORT3=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

echo "----- Executing SBD @ " `date` > $PORT3

#####################################
echo "switching on IRD" > $PORT3
/mnt/gpio/ird_ON
sleep 20
echo "switching on RS232" > $PORT3
/mnt/gpio/rs232_ON
sleep 2
echo "switching on SBD pin" > $PORT3
/mnt/gpio/sbd_ON
sleep 2
############# 
echo $1
/mnt/sbd/sbd_file_send_ascii $1
#############

/mnt/gpio/sbd_OFF
/mnt/gpio/ird_OFF
/mnt/gpio/rs232_OFF

echo "all done " > $PORT3


