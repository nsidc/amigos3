#!./bin/bash
i="0"
while [ $i -le 59 ]
do

dividor=4095
multiplier=790
final_dividor=100

echo 5 > /sys/class/gpio/mcp3208-gpio/index

cat /sys/class/gpio/mcp3208-gpio/data >/media/mmcblk0p1/amigos/amigos/logs/current_hex

awk '{print ("0x"$1)+0 } ' /media/mmcblk0p1/amigos/amigos/logs/current_hex >/media/mmcblk0p1/amigos/amigos/logs/current_dec
current=$(cat /media/mmcblk0p1/amigos/amigos/logs/current_dec)
time_now="$(date)"
echo $current $multiplier $dividor $final_dividor $time_now| awk '{ printf("%s, %2.3f\n",$time_now,  ((($1*$2)/$3)/$4)) }' >> /media/mmcblk0p1/amigos/amigos/logs/current.log

sleep 1
i=$(($i+1));
done