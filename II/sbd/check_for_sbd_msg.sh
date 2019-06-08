#!/bin/sh

TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
DATETIME=`date +%H%M_%m%d%y`
ID=/root/station
need_eth_file=/var/tmp/NO_ETH
PORT=/dev/ttyS3
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

echo "" > $PORT
echo "----- Executing $station, $caller, `date`" > $PORT
echo "----- Executing $station, $caller, `date`" >> /mnt/logs/sbd_msgs

/mnt/sbd/set_sbd_ttyS1

if [ -s /var/tmp/sbd ] ; then

	# +SBDIX: 0, 32940, 1, 8, 26, 0 OR +SBDIX: 0, 3206, 1, 4, 12, 0 or +SBDIX: 0, 3208, 0, 0, 0, 0
	# means a message and 26 bytes long
	sed 's/,/ /g' /var/tmp/sbd > /var/tmp/sbda
	grep +SBDIX: /var/tmp/sbda > /var/tmp/sbd_msg
	awk ' $1 == "+SBDIX:" {FS="," ; printf "%s\n", $2} ' /var/tmp/sbd_msg > /var/tmp/sbd_msg_MO_status
	awk ' $1 == "+SBDIX:" {FS="," ; printf "%s\n", $4} ' /var/tmp/sbd_msg > /var/tmp/sbd_msg_flag
	awk ' $1 == "+SBDIX:" {FS="," ; printf "%s\n", $6} ' /var/tmp/sbd_msg > /var/tmp/sbd_msg_length
	# cat /var/tmp/sbd_msg_flag
	# cat /var/tmp/sbd_msg_length
	x=$(cat /var/tmp/sbd_msg_flag)
	y=$(cat /var/tmp/sbd_msg_length)
	z=$(cat /var/tmp/sbd_msg_MO_status)
	
	if [ $x == 1 ] ; then
		echo "******* SBD message pending of length $y characters" > $PORT
		echo "******* SBD message pending of length $y characters, `date`" >> /mnt/logs/sbd_msgs
		# get message
		/mnt/sbd/get_sbd_ttyS1
		# message left in /var/tmp/sbd2
		# /var/tmp/process_sbd_msg.sh
		else
		echo "##### NO SBD message pending, MO status=$z, MT status=$x " > $PORT
		echo "##### NO SBD message pending, MO status=$z, MT status=$x, `date`" >> /mnt/logs/sbd_msgs
		# rm /var/tmp/sbd*
	fi
else 
	echo "xxxxxxx TIMEOUT or ERROR in getting SBD" > $PORT
	echo "xxxxxxx TIMEOUT or ERROR in getting SBD, `date` " >> /mnt/logs/sbd_msgs
	# rm /var/tmp/sbd*
fi
#
echo "----- $station, $caller exit, `date`" > $PORT
#
exit


