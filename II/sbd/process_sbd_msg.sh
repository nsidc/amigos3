#!/bin/sh

TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
DATETIME=`date +%H%M_%m%d%y`
ID=/root/station
need_eth_file=/var/tmp/NO_ETH
PORT=/dev/ttyS3
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

cron_loc=/media/mmcblk0/cron

#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

echo "" > $PORT
echo "----- Executing $station, $caller, `date`" > $PORT

# $CMD 911 Z
# typical message 911 means reboot
###############
if [ -f /var/tmp/sbd2 ] ; then
	awk ' $1 == "$CMD" {printf "%s\n", $2} ' /var/tmp/sbd2 > /var/tmp/sbd_cmd
	x=$(cat /var/tmp/sbd_cmd)
#
	case "$x" in
	   "911") echo "------- 911 Means REBOOT" > $PORT
		      echo "******* Rxd 911 = REBOOT, `date` " >> /mnt/logs/sbd_msgs 
		      /sbin/reboot &	  	
	   	  ;;
	   "711") echo "------- 711 Means HALT"  > $PORT
	   		  echo "******* Rxd 711 = HALT, `date` " >> /mnt/logs/sbd_msgs
	   		  /sbin/halt &
	      ;;
	   "511") echo "------- 511 Means SWITCH CRONTAB from SUMMER to WINTER" > $PORT
	    	  echo "******* Rxd 511 = SWITCH CRONTAB from SUMMER to WINTER, `date` " >> /mnt/logs/sbd_msgs
	    	  cp $cron_loc/root.full.winter $cron_loc/root.full ;
	    	  crontab $cron_loc/root.full ;
	    	  mrw ; touch /mnt/SUMMER ;
	          mv /mnt/SUMMER /mnt/WINTER ;
	          mro ;
	      ;;
	   "311") echo "------- 311 Means SWITCH CRONTAB from WINTER to SUMMER" > $PORT
	          echo "******* Rxd 311 = SWITCH CRONTAB from WINTER to SUMMER, `date` " >> /mnt/logs/sbd_msgs
	          cp $cron_loc/root.full.summer $cron_loc/root.full ;
	          crontab $cron_loc/root.full ;
	          mrw ; touch /mnt/WINTER ;
	          mv /mnt/WINTER /mnt/SUMMER ;
	          mro ;
	   	  ;;
	   "111") echo "------- 111 Means GPS CYCLE" > $PORT
	   		  /mnt/gps/gps.sh &
	          echo "******* Rxd 111 = GPS CYCLE, `date` " >> /mnt/logs/sbd_msgs
	   	  ;;
	esac

# rm /var/tmp/sbd*
else
echo "xxxxx NO SBD message to process" > $PORT
fi
###############
#
echo "----- $station, $caller exit, `date`" > $PORT
#
exit

