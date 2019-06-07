#!/bin/sh
PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2

# echo "Testing SBD mode over ttyS1!! `date` " > $PORT
`stty -F $PORT1 cs8 9600`
/mnt/gpio/iridium_ON
/mnt/gpio/memsic_ON

sleep 30
echo "" > $PORT1
echo "atz" > $PORT1
sleep 20
echo "sending sbdwt " > $PORT
echo "at+sbdwt= `cat /var/weather` " > $PORT1
sleep 10
echo "sending sbdi " > $PORT
echo "at+sbdi" > $PORT1
sleep 20
echo "ended SBD mode" > $PORT
/mnt/gpio/memsic_OFF
/mnt/gpio/iridium_OFF
