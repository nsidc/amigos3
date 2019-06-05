#!/bin/sh
#!/usr/bin/awk -f
# modified for Triton3 by RR @ RB 23rd Feb 2014

# grab ps and store to /var/tmp/ps_log

SBD=/var/tmp/SBD_status 
IRD=/var/tmp/IRD_status 

status=`cat $SBD`

echo "##################" >> /var/tmp/ps_log
echo "" >> /var/tmp/ps_log
date >> /var/tmp/ps_log
echo "" >> /var/tmp/ps_log
ps >> /var/tmp/ps_log
echo "" >> /var/tmp/ps_log
status=`cat $SBD`
echo "SBD = $status " >> /var/tmp/ps_log
status=`cat $IRD`
echo "IRD = $status " >> /var/tmp/ps_log


