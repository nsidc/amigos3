#!/bin/sh
#
# Genesis RR @ RB 17th May 2014 test for ethernet coming up ok

PORT=/dev/ttyS3
TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
ID=/root/station
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
eth_stat=0

echo ">>>>> Executing $caller @ `date`" > $PORT

#####################################
#
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

sleep 10
eth_stat=`/sbin/route | wc -l`

if [ $eth_stat == 4 ] ; then
	echo "----- $station, eth_stat = $eth_stat, ETH0 configured ok, `date` " > $PORT
	echo "----- $station, eth_stat = $eth_stat, ETH0 configured ok, `date` " >> /mnt/logs/eth_status
	echo "----- $station, eth_stat = $eth_stat, ETH0 configured ok, `date` " >> /var/tmp/eth_status
else
	echo "----- $station, eth_stat = $eth_stat, ETH0 not configured ok, `date` " > $PORT
	echo "----- $station, eth_stat = $eth_stat, ETH0 not configured ok, `date` " >> /mnt/logs/eth_status
	echo "----- $station, eth_stat = $eth_stat, ETH0 not configured ok, `date` " >> /var/tmp/eth_status
sleep 5
/sbin/reboot		
fi
echo "<<<<< Executing $caller exit @ `date`" > $PORT
exit 0
