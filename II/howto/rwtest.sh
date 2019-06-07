#!/bin/sh

PORT=/dev/ttyS3

x=1
t=10
while [ $x -le $t ]
do
echo "RW times = " $x  > $PORT
date
mount / -o remount,rw
touch /root/file$x
sleep 1
sync
sleep 1
mount / -o remount,ro
x=$(( $x + 1 ))
echo ""
sleep 5
done

echo " reboot in 10 seconds" > $PORT
sleep 10

/sbin/reboot

