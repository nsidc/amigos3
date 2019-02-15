mount / -o remount,rw
cp /mnt/S82ron.sh.in_A2_firnaqua_summer /etc/rc2.d/S82ron.sh
chmod +x /etc/rc2.d/S82ron.sh
mount / -o remount,ro

cp /mnt/sked/schedule.dat.summer /mnt/sked/schedule.dat
cp /mnt/sked/schedule.dat.summer /var/schedule.dat
