#!/bin/sh
#!/usr/bin/awk -f

PORT=/dev/ttyS3
ID=/root/station
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
station=`cat $ID`

#############
if [ $station == 'Wx7' ]  ; then HOST=192.168.0.20 ; PORT=8082 ; fi
if [ $station == 'Wx8' ]  ; then HOST=192.168.0.20 ; PORT=8082 ; fi
if [ $station == 'Wx11' ] ; then HOST=192.168.0.22 ; PORT=8084 ; fi
if [ $station == 'Wx14' ] ; then HOST=192.168.0.20 ; PORT=8082 ; fi

# 2009 Nov 5 Terry Haran
# Updated ftp ip address for sidads.colorado.edu
#
# 2009 Nov 9 Terry Haran
# fixed ftp ip address for sidads.colorado.edu
# changed back IPA to thistle.org
# modified for Triton3 by RR @ RB 6th Feb 2013

ppid=0

# allow the FTP to run for 20 minutes
sleep 3

ps > /var/tmp/ps.txt

grep "http://$HOST:$PORT/command/" /var/tmp/ps.txt | awk '{ print $1 ; }' > /var/tmp/ps2.txt
ppid=`tail -1 /var/tmp/ps2.txt 2>/dev/null`

if [ -s /var/tmp/ps2.txt ] ; then
echo "ppid = " $ppid
kill $ppid
fi

exit 0

