#!/bin/sh

HOST='192.168.0.80'
dummy_tries=5
ID=/root/station
PORT=/dev/ttyS0
dummy_tries=50

dummy='http://192.168.0.80/dummy'
LOGFILE="/mnt/temp_images/garage.log"

/mnt/gpio/hub_OFF
sleep 2
/mnt/gpio/hub_ON
sleep 40

ifconfig eth0 up
sleep 1
ifconfig eth0 up
route add default gw 192.168.0.1
sleep 1

# get what AMIGOS unit this is and form account and passwd
station=`cat $ID`

if [ $station == 'amigos1' ] ; then HOST='192.168.0.80' ; fi
if [ $station == 'KA2' ] ; then HOST='192.168.0.80' ; fi

echo station is $station " " host is $HOST dummy is $dummy 

USER=root

##################
cd /mnt/upload_images/
rm *
cp /mnt/temp_images/test.jpg . 
mv test.jpg TEST_`date +\%H\%M_\%m\%d\%y`.jpg

################### Script to keep trying to wget dummy before FTP begins, dummy must be non-zero

if [ $dummy_tries -gt 0 ] ; then
i=1
while [ ! -s dummy ] && [ $i -le $dummy_tries ]
do   
echo "in the wget loop" >> $LOGFILE
wget $dummy -O dummy
echo "times thru loop $i" >> $LOGFILE
i=`expr $i + 1`
done
if [ ! -s dummy ] ; then
echo "unable to wget `date` $dummy in $dummy_tries attempts" >> $LOGFILE
# exit 1
else
echo "out of wget loop `date` after $i attempts" >> $LOGFILE
fi
fi
###############

ls -lrt TEST*.jpg | head -4 > last4_jpgs
awk '{print $9}' last4_jpgs > last4_pics
FILE1=`cat last4_pics | awk 'NR==1 {print $1;}'` 
FILE2=`cat last4_pics | awk 'NR==2 {print $1;}'`

echo $FILE1 > $PORT 

/mnt/sked_tasks/ps_check &

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd /mnt/temp_images/
passive
ascii
put $FILE1
quit
END_SCRIPT
sleep 120
ifconfig eth0 down
/mnt/gpio/hub_OFF
exit 0



