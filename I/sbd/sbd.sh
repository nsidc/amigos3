#!/bin/sh  

# modified at RB on April 4th 2009  

PORT=/dev/ttyS0 
PORT2=/dev/ttyS2  

############ only additions
/mnt/gpio/iridium_ON
sleep 1
/mnt/gpio/memsic_ON
echo sleeping for 30s
sleep 32
#####################

# switch on RS232 
/mnt/gpio/rs232_ON  

echo "Testing SBD mode over ttyS2!! 
`date` " > $PORT 
sleep 10 

echo "sending sbdwt " > $PORT  

########## new for PCAM  
# get the first line in voltagedata and 
# then get every 60th ie hourly line  

awk 'NR == 1' /var/voltagedata > /var/foo1 
awk 'NR %10 == 0' /var/voltagedata >> /var/foo1  

gzip /var/foo1  

/mnt/sbd/sbd_file_send /var/foo1.gz  

rm /var/foo1.gz  
sleep 35 

##########  
echo "ended SBD mode" > $PORT 

# RS232 off 
/mnt/gpio/rs232_OFF
  
############ only additions
/mnt/gpio/iridium_OFF
/mnt/gpio/memsic_OFF
#####################
