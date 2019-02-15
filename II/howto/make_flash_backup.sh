#!/bin/sh

# Modified for SDAC and Triton3

PORT=/dev/ttyS3
DATE=`date +%H%Mz-%m%d-%Y`
ID=/root/station

# get what AMIGOS unit this is
station=`cat $ID`
SRC=/media/mmcblk0/
DEST=/media/mmcblk0/bak/

cd /var/tmp

echo "----- Executing Backup of /media/mmcblk0/ @ " `date` > $PORT
echo "----- Filename will be Flash-$station-$DATE.tgz" > $PORT
echo "----- Make sure data and time are set correctly...waiting 3 secs" > $PORT
sleep 3

tar -czvf Flash-$station-$DATE.tgz $SRC

echo "----- Copying Flash-$station-$DATE.tgz to $DEST" > $PORT
cp Flash-$station-$DATE.tgz $DEST

echo "All done " > $PORT

