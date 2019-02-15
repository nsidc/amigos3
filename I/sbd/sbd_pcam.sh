#!/bin/sh

# modified at RB on April 4th 2009

PORT=/dev/ttyS0
PORT2=/dev/ttyS2

# switch on RS232
/mnt/gpio/rs232_ON

echo "Testing SBD mode over ttyS2!! `date` " > $PORT
sleep 10
echo "sending sbdwt " > $PORT

########## new for PCAM
/mnt/sbd/sbd_file_send /mnt/sbd/foo.zip
sleep 32
##########

echo "ended SBD mode" > $PORT
# RS232 off
/mnt/gpio/rs232_OFF

