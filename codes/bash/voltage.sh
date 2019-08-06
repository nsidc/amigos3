#!./bin/bash
i="0"
Vref_10=33
Tdividor=1000
Vdividor=4095
Idividor=4095
# was Vmultiplier=7987
Vmultiplier=7997
Vfinal_dividor=10000
Imultiplier=790
Ifinal_dividor=100
dividor=4095
multiplier=790
final_dividor=100

while [ $i -le 50 ]
do

echo 4 > /sys/class/gpio/mcp3208-gpio/index

cat /sys/class/gpio/mcp3208-gpio/data >/media/mmcblk0p1/logs/voltage_hex

awk '{print ("0x"$1)+0 } ' /media/mmcblk0p1/logs/voltage_hex >/media/mmcblk0p1/logs/voltage_dec
voltage=$(cat /media/mmcblk0p1/logs/voltage_dec)
time_now="$(date)"
echo $voltage $Vref_10 $Vdividor $Vmultiplier $Vfinal_dividor $time_now| awk '{ printf("%s, %2.3f\n",$time_now,  ((($1*$2)/$3)*$4)/$5 ) }' >> /media/mmcblk0p1/logs/voltage.log

sleep 1

echo 5 > /sys/class/gpio/mcp3208-gpio/index
cat /sys/class/gpio/mcp3208-gpio/data >/media/mmcblk0p1/logs/current_hex

awk '{print ("0x"$1)+0 } ' /media/mmcblk0p1/logs/current_hex >/media/mmcblk0p1/logs/current_dec
current=$(cat /media/mmcblk0p1/logs/current_dec)
time_now="$(date)"
echo $current $multiplier $dividor $final_dividor $time_now| awk '{ printf("%s, %2.3f\n",$time_now,  ((($1*$2)/$3)/$4)) }' >> /media/mmcblk0p1/logs/current.log

i=$(($i+1));
done
