#!/bin/sh

x=1
t=4000
dial_cmd="ATDT"

/mnt/gpio/iridium_OFF
sleep 1
/mnt/gpio/memsic_OFF
sleep 1

echo " Begin Dial Test of Iridium number " $1

while [ $x -lt $t ]
do
echo "------------------------"
echo "loop count = " $x
/mnt/gpio/iridium_ON
/mnt/gpio/memsic_ON
sleep 20
./com_test $dial_cmd$1
/mnt/gpio/iridium_OFF
/mnt/gpio/memsic_OFF
sleep 5
let "x +=1"
done

