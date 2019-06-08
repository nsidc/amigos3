#!/bin/sh
PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2
ID=/root/station

# set up the compact flash card SET for correct AMIGOS number!!!!!!!!!!!!!
HOUR_NOW=`date +%H`

# allow the schedule checker time to set the Iridium status
sleep 20

# get what AMIGOS unit this is
station=`cat $ID`

######## check Iridium status first ########

IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
#####################################

while [ $SBD == 1 ]
do
echo "SBD in use, waiting " `date` 
echo "SBD in use, waiting " `date` > $PORT
sleep 21
SBD=`cat $SBD_status`
done

echo "SBD is now free " `date` 
echo "SBD is now free " `date` > $PORT
#####################################
echo "1" > $SBD_status
#####################################

while [ $IRD == 1 ]
do
echo "Iridium in use, waiting " `date` 
echo "Iridium in use, waiting " `date` > $PORT
sleep 21
IRD=`cat $IRD_status`
done

echo "Iridium is now free " `date` 
echo "Iridium is now free " `date` > $PORT

################################### just in case things had been power cycle or in winter -> ON
# if [ -f /mnt/SUMMER ] ; then
# fi

/mnt/gpio/rs232_ON
/mnt/gpio/wxt_ON
echo "WXT & RS232 ON" > $PORT

#####################################

sleep 30
/mnt/weather/getweather_tty2
/mnt/gpio/wdt_tick

############# merge the voltage file and the weather file to make a file called foo (for now)

awk '{ print $3; print $4; print $5; print $6 }' /var/voltage > /var/foo
x=$(cat /var/foo)
y=$(cat /var/weather)

echo $station $y $x > /var/foo
echo $y $x >> /var/foodata

############# now send the data out as sbd data, first need to turn off WXT

/mnt/gpio/wxt_OFF
echo "WXT OFF" > $PORT
sleep 3

# only do SBD if at the midnight hour
if [ $HOUR_NOW == 08 ] ; then

# echo "Testing SBD mode over ttyS1!! `date` " > $PORT
`stty -F $PORT1 cs8 9600`
/mnt/gpio/iridium_ON
echo "iridium on" > $PORT
/mnt/gpio/memsic_ON
echo "memsic on" > $PORT

sleep 31

# ----------------------------
cd /var
cp foodata winterdata
gzip winterdata
echo "calling send_sbd_file" > $PORT
/mnt/weather/sbd_file_send /var/winterdata.gz
rm /var/winterdata.gz
#-----------------------------

sleep 32
echo "ended SBD winter mode" > $PORT
/mnt/gpio/memsic_OFF
/mnt/gpio/iridium_OFF
/mnt/gpio/rs232_OFF
sleep 3

######### end of the condition
fi

######## check to see if this should go back on 
if [ -f /mnt/SUMMER ] ; then
/mnt/gpio/rs232_ON
/mnt/gpio/wxt_ON
echo "WXT & RS232 ON" > $PORT
fi
sleep 3
#########################
# clear the busy flag
echo "0" > $SBD_status

