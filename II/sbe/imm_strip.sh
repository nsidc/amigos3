#!/bin/sh

TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
DATETIME=`date +%H%M_%m%d%y`
ID=/root/station
need_eth_file=/var/tmp/NO_ETH
PORT=/dev/ttyS3
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`
#
dev_file41=/var/tmp/device41
dev_file42=/var/tmp/device42
dev_file77=/var/tmp/device77
dev_file78=/var/tmp/device78
#
#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

echo "" > $PORT
echo ">>>>> Executing $station, $caller, `date`" > $PORT
echo "----- Processing IMM data files," `date` > $PORT

# SBE41 012815 150239 <RemoteReply> 12941,   0.5983,  17.3685,   -1.730, 22:02:38, 01-28-2015
# SBE41 101416 015701 <RemoteReply> 12941,   0.0896,  19.1503,   -1.660, 01:58:03, 14-10-2016
# ACQ77 012815 150249 SampleData ID='0x00000018' Len='109' CRC='0x9487085C'> 1 28 2015 15 0 0 0 48 -0.241 
# 0.197 0.491 18 17 17 13.0 1527.7 240.7 -28.7 22.9 0.000 22.39 0 0 0.311 309.3

# First process Seabirds raw format is:
# SBE41 012815 150239 <RemoteReply> 12941,   0.5983,  17.3685,   -1.730, 22:02:38, 01-28-2015
# SBE41, 040515, 215916, <RemoteReply> 12941,   0.4269,  16.6216,   -1.841, 21:56:37, 04-05-2015
# get rid of extraneous <RemoteReply> string and Seabird serial number
# SBE41, 040515, 215916,  12941,   0.4269,  16.6216,   -1.841, 21:56:37, 04-05-2015
sed 's/<RemoteReply>//g' /var/tmp/imm > /var/tmp/imm2
# awk ' $4 == "12941," {FS="," ; printf "%s%s%s%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe41
awk ' $4 == "12941," {FS="," ; printf "%s,%s,%s,%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe41
# remove ','
sed 's/,/ /g' /var/tmp/sbe41 > /var/tmp/sbe41a
# replace ':' in time string
sed 's/:/ /g' /var/tmp/sbe41a > /var/tmp/sbe41b
# change date from MM-DD-YYYY to MMDD YYYY then cat those two after stripping the 2000 year 
sed 's|\([0-1][0-9]\)-\([0-3][0-9]\)-\([0-2][0-9][0-9][0-9]\)|\1\2 \3|g' /var/tmp/sbe41b > /var/tmp/sbe41c
# bring together time discrete pieces to one string
awk '$1 == "SBE41" {printf "%s %s %s %s %s %s %s %s\n", $1,$2,$3,$4($5-2000),$6$7$8,$9,$10,$11}' /var/tmp/sbe41c > /var/tmp/sbe41d
#
if [ -f $dev_file41 ] ; then
echo "SBE41 $DATE $TIME ERROR in IMM comms" > /var/tmp/sbe41d
cat /var/tmp/sbe41d >> /var/tmp/immdata
else
cat /var/tmp/sbe41d >> /var/tmp/immdata
fi
# rm /var/tmp/sbe41a
# rm /var/tmp/sbe41b
# rm /var/tmp/sbe41c
#
# First process Seabirds raw format is:
# SBE42 012815 150239 <RemoteReply> 12942,   0.5983,  17.3685,   -1.730, 22:02:38, 01-28-2015
# get rid of extraneous <RemoteReply> string and Seabird serial number
# awk ' $4 == "12942," {FS="," ; printf "%s%s%s%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe42
awk ' $4 == "12942," {FS="," ; printf "%s,%s,%s,%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe42
# remove ','
sed 's/,/ /g' /var/tmp/sbe42 > /var/tmp/sbe42a
# replace ':' in time string
sed 's/:/ /g' /var/tmp/sbe42a > /var/tmp/sbe42b
# change date from MM-DD-YYYY to MMDD YYYY then cat those two after stripping the 2000 year 
sed 's|\([0-1][0-9]\)-\([0-3][0-9]\)-\([0-2][0-9][0-9][0-9]\)|\1\2 \3|g' /var/tmp/sbe42b > /var/tmp/sbe42c
# bring together time discrete pieces to one string
# SBE42 012815 152245 0128 2015 22 22 43 0.5998 17.4761 -1.480
awk '$1 == "SBE42" {printf "%s %s %s %s %s %s %s %s\n", $1,$2,$3,$4($5-2000),$6$7$8,$9,$10,$11}' /var/tmp/sbe42c > /var/tmp/sbe42d
#
if [ -f $dev_file42 ] ; then
echo "SBE42 $DATE $TIME ERROR in IMM comms" > /var/tmp/sbe42d
cat /var/tmp/sbe42d >> /var/tmp/immdata
else
cat /var/tmp/sbe42d >> /var/tmp/immdata
fi
#
cp /var/tmp/immdata /mnt/saved_images/immdata
# rm /var/tmp/sbe42a
# rm /var/tmp/sbe42b
# rm /var/tmp/sbe42c
#
awk ' $1 == "ACQ77" {printf "%s %s %s %02d %02d %s %s %02d %02d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \
%s\n", $1,$2,$3,$8,$9,($10-2000),$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28, \
$31,$32} ' /var/tmp/imm > /var/tmp/acq77
#
awk ' $1 == "ACQ77" {printf "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n", $1,$2,$3,$4$5$6, $7$8$9, $12,$13,\
$14,$18,$19,$20,$21,$22,$23,$24,$25,$26} ' /var/tmp/acq77 > /var/tmp/acq77a
#
if [ -f $dev_file77 ] ; then
echo "ACQ77 $DATE $TIME ERROR in IMM comms" > /var/tmp/acq77b
else
sed 's/,//g' /var/tmp/acq77a > /var/tmp/acq77b
fi
#
cat /var/tmp/acq77b >> /var/tmp/immdata
#
awk ' $1 == "ACQ78" {printf "%s %s %s %02d %02d %s %s %02d %02d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \
%s\n", $1,$2,$3,$8,$9,($10-2000),$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28, \
$31,$32} ' /var/tmp/imm > /var/tmp/acq78
#
awk ' $1 == "ACQ78" {printf "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n", $1,$2,$3,$4$5$6, $7$8$9, $12,$13,\
$14,$18,$19,$20,$21,$22,$23,$24,$25,$26} ' /var/tmp/acq78 > /var/tmp/acq78a
#
if [ -f $dev_file78 ] ; then
echo "ACQ78 $DATE $TIME ERROR in IMM comms" > /var/tmp/acq78b
else
sed 's/,//g' /var/tmp/acq78a > /var/tmp/acq78b
fi
#
cat /var/tmp/acq78b >> /var/tmp/immdata
#
cp /var/tmp/immdata /mnt/saved_images/immdata
##############
if [ ! -f $need_eth_file ] ; then
echo "----- Ethernet is UP " > $PORT
cp /var/tmp/immdata /root/workspace/
else
echo "----- Ethernet is DOWN" > $PORT
fi
##############
# rm imm2
echo "----- Processing all done," `date` > $PORT
# skip the SBD messaging for now
# echo "----- skip SBD messaging for now," `date` > $PORT
# 
#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################
echo "----- switching on IRD" > $PORT
/mnt/gpio/ird_ON
sleep 15
echo "----- switching on SBD pin" > $PORT
/mnt/gpio/sbd_ON
############# SBE41
y=$(cat /var/tmp/sbe41d)
echo $station "IMM" $y > /var/tmp/sbe41e
#############
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/sbe41e
sleep 30
############# SBE42
y=$(cat /var/tmp/sbe42d)
echo $station "IMM" $y > /var/tmp/sbe42e
#############
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/sbe42e
sleep 30
############# ACQ77
y=$(cat /var/tmp/acq77b)
echo $station "IMM" $y > /var/tmp/acq77c
#############
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/acq77c
sleep 30
############# ACQ78
y=$(cat /var/tmp/acq78b)
echo $station "IMM" $y > /var/tmp/acq78c
#############
# now send wxt data through SBD mode
/mnt/sbd/sbd_file_send_ascii /var/tmp/acq78c
sleep 30
#############
echo "<<<<< $station, $caller exit, `date`" > $PORT
#####################################
exit 0
