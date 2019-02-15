#!/bin/sh
PORT=/dev/ttyS0
PORT1=/dev/ttyS1
PORT2=/dev/ttyS2

# echo "Testing SBD mode over ttyS1!! `date` " > $PORT
`stty -F $PORT1 cs8 9600`

while true
do
echo "u" > $PORT1
done

