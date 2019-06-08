#!/bin/sh

TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
DATETIME=`date +%H%M_%m%d%y`
ID=/root/station
PORT=/dev/ttyS3

sed 's/<RemoteReply>//g' /var/tmp/imm > /var/tmp/imm2
awk ' $4 == "12941," {FS="," ; printf "%s%s%s%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe41
# remove ','
sed 's/,/ /g' /var/tmp/sbe41 > /var/tmp/sbe41a
# replace ':' in time string
sed 's/:/ /g' /var/tmp/sbe41a > /var/tmp/sbe41b
# change date from MM-DD-YYYY to MMDD YYYY then cat those two after stripping the 2000 year 
sed 's|\([0-1][0-9]\)-\([0-3][0-9]\)-\([0-2][0-9][0-9][0-9]\)|\1\2 \3|g' /var/tmp/sbe41b > /var/tmp/sbe41c
# bring together time discrete pieces to one string
awk '$1 == "SBE41" {printf "%s %s %s %s %s %s %s %s\n", $1,$2,$3,$4($5-2000),$6$7$8,$9,$10,$11}' /var/tmp/sbe41c > /var/tmp/sbe41d
cat /var/tmp/sbe41d >> /var/tmp/immdata
rm /var/tmp/sbe41a
rm /var/tmp/sbe41b
rm /var/tmp/sbe41c
#
# First process Seabirds raw format is:
# SBE42 012815 150239 <RemoteReply> 12942,   0.5983,  17.3685,   -1.730, 22:02:38, 01-28-2015
# get rid of extraneous <RemoteReply> string and Seabird serial number
awk ' $4 == "12942," {FS="," ; printf "%s%s%s%s,%s%s%s%s\n", $1,$2,$3,$9,$8,$5,$6,$7} ' /var/tmp/imm2 > /var/tmp/sbe42
# remove ','
sed 's/,/ /g' /var/tmp/sbe42 > /var/tmp/sbe42a
# replace ':' in time string
sed 's/:/ /g' /var/tmp/sbe42a > /var/tmp/sbe42b
# change date from MM-DD-YYYY to MMDD YYYY then cat those two after stripping the 2000 year 
sed 's|\([0-1][0-9]\)-\([0-3][0-9]\)-\([0-2][0-9][0-9][0-9]\)|\1\2 \3|g' /var/tmp/sbe42b > /var/tmp/sbe42c
# bring together time discrete pieces to one string
# SBE42 012815 152245 0128 2015 22 22 43 0.5998 17.4761 -1.480
awk '$1 == "SBE42" {printf "%s %s %s %s %s %s %s %s\n", $1,$2,$3,$4($5-2000),$6$7$8,$9,$10,$11}' /var/tmp/sbe42c > /var/tmp/sbe42d
cat /var/tmp/sbe42d >> /var/tmp/immdata
cp /var/tmp/immdata /mnt/saved_images/immdata
rm /var/tmp/sbe42a
rm /var/tmp/sbe42b
rm /var/tmp/sbe42c
# rm imm2
# 
awk ' $1 == "ACQ77," {printf "%s %s %s %02d %02d %s %s %02d %02d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \
%s\n", $1,$2,$3,$8,$9,($10-2000),$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28, \
$31,$32} ' /var/tmp/imm > /var/tmp/acq77
#
awk ' $1 == "ACQ77," {printf "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n", $1,$2,$3,$4$5$6, $7$8$9, $12,$13,\
$14,$18,$19,$20,$21,$22,$23,$24,$25,$26} ' /var/tmp/acq77 > /var/tmp/acq77a
sed 's/,//g' /var/tmp/acq77a > /var/tmp/acq77b
cat /var/tmp/acq77b >> /var/tmp/immdata
#
awk ' $1 == "ACQ78," {printf "%s %s %s %02d %02d %s %s %02d %02d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \
%s\n", $1,$2,$3,$8,$9,($10-2000),$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28, \
$31,$32} ' /var/tmp/imm > /var/tmp/acq78
#
awk ' $1 == "ACQ78," {printf "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n", $1,$2,$3,$4$5$6, $7$8$9, $12,$13,\
$14,$18,$19,$20,$21,$22,$23,$24,$25,$26} ' /var/tmp/acq78 > /var/tmp/acq78a
sed 's/,//g' /var/tmp/acq78a > /var/tmp/acq78b
cat /var/tmp/acq78b >> /var/tmp/immdata
#
cp /var/tmp/immdata /mnt/saved_images/immdata
rm imm2
echo "Processing all done " `date` > $PORT

exit 0
##########