#
# bootmisc.sh	Miscellaneous things to be done during bootup.
#

. /etc/default/rcS
#
# Put a nologin file in /etc to prevent people from logging in before
# system startup is complete.
#
if test "$DELAYLOGIN" = yes
then
  echo "System bootup in progress - please wait" > /etc/nologin
  cp /etc/nologin /etc/nologin.boot
fi

#
# Set pseudo-terminal access permissions.
#
if ( ! grep -q devfs /proc/mounts ) && test -c /dev/ttyp0
then
	chmod 666 /dev/tty[p-za-e][0-9a-f]
	chown root:tty /dev/tty[p-za-e][0-9a-f]
fi

#
# Apply /proc settings if defined
#
SYSCTL_CONF="/etc/sysctl.conf"
if [ -f "${SYSCTL_CONF}" ]
then
	if [ -x "/sbin/sysctl" ]
	then
		/sbin/sysctl -p "${SYSCTL_CONF}"
	else
		echo "To have ${SYSCTL_CONF} applied during boot, install package <procps>."
	fi
fi

#
# Update /etc/motd.
#
if test "$EDITMOTD" != no
then
	uname -a > /etc/motd.tmp
	sed 1d /etc/motd >> /etc/motd.tmp
	mv /etc/motd.tmp /etc/motd
fi

#
# This is as good a place as any for a sanity check
# /tmp should be a symlink to /var/tmp to cut down on the number
# of mounted ramdisks.
if test ! -L /tmp && test -d /var/tmp
then
	rm -rf /tmp
	ln -sf /var/tmp /tmp
fi

#
# Update dynamic library cache, but only if ld.so.conf is present
#
if [ -e /etc/ld.so.conf ] ; then
	/sbin/ldconfig
fi

# Set the system clock from hardware clock
# If the timestamp is 1 day or more recent than the current time,
# use the timestamp instead.
/etc/init.d/hwclock.sh start
if test -e /etc/timestamp
then
	SYSTEMDATE=`date "+%Y%m%d"`
	TIMESTAMP=`cat /etc/timestamp | awk '{ print substr($0,9,4) substr($0,1,4);}'`
        NEEDUPDATE=`expr \( $TIMESTAMP \> $SYSTEMDATE \)`                                                 
        if [ $NEEDUPDATE -eq 1 ]; then 
		date `cat /etc/timestamp`
		/etc/init.d/hwclock.sh stop
	fi
fi

######################
#
# added these flags settings, VCHK_status, aws_mode, reset_flag, sleep_flag, by RR @ 10th St 8/6/16
#
# initialize the ethernet hub and touch some files
ID=/root/station
station=`cat $ID`
PORT=/dev/ttyS3

/root/gpio/gpio.sh hub_ON
/root/gpio/gpio.sh SERIAL_ENA_ON

# init some status files

# set the schedule file
if [ -s /mnt/sked/schedule.dat ] ; then
cp /mnt/sked/schedule.dat /var/tmp/schedule.dat 
else
cp /root/schedule.dat /mnt/sked/schedule.dat
cp /root/schedule.dat /var/tmp/schedule.dat
fi
#########
echo 0 > /var/tmp/voltage_status
echo 0 > /var/tmp/IRD_status
echo 0 > /var/tmp/SBD_status
echo 0 > /var/tmp/TPS_status
echo 0 > /var/tmp/ftp_upload_completion_flag
echo 0 > /var/tmp/ftp_upload_tps_completion_flag
echo 0 > /var/tmp/VCHK_status
echo 0 > /var/tmp/aws_mode
echo 1 > /var/tmp/reset_flag
echo 0 > /var/tmp/sleep_flag
####################
# store the power-up date and time and append to repower file
echo ----- $station RE-POWERING @ `date` >> /mnt/logs/repower_hist
touch /var/tmp/repower_hist
dmesg >> /var/tmp/repower_hist

# /etc/init.d/inetd start
# /etc/init.d/sshd start

# start up the cronjobs
#############
cron start
cp /media/mmcblk0/cron/root.full /var/cron/tabs/root
/usr/bin/crontab /var/cron/tabs/root
sleep 5
/usr/bin/crontab /var/cron/tabs/root
rm /var/cron/log 
ln -s /var/tmp/log /var/cron/log
# touch /var/tmp/NO_ETH
#############
if [ -f /mnt/SUMMER ] ; then
/mnt/gpio/summer_devices_ON
else
/mnt/gpio/winter_devices_ON
fi
#############
mount -t nfs -o nolock 192.168.0.47:/var/nfs /root/workspace
#############
: exit 0
