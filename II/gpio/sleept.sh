#!/bin/sh

PORT3=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station

station=`cat $ID`
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

sleep 120

/mnt/sleep/sleep.sh +0:03

