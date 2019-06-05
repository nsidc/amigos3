#!/bin/sh

# modified by RR 12/19/06 to archive data
# modified by RR 9/29/07 @ Mona Vale for Wx7
# modified by RR 11/17/08 @ Rose Bay for Wx8 to keep winter data in RAM
#
# 2010/01/11 Terry Haran
# Changed weather to wxt.
# Added csi.
# Added removal of single line files from /var
#
# 2010/01/12 Terry Haran
# Added altdata.
#
# 2010/01/17 Terry Haran
# Added clearing GRS_status.
#
# 2010/01/30 Terry Haran
# Uncommented copying date-stamped backup files to /mnt/saved_images.
#
# 2010 Oct 25 Terry Haran
# Changed date/time format.
# Removed checking for SUMMER.
# Simplified gzipping.
# Added gzipping, date stamping, and saving repower_hist and upload_hist.
#
# 2010 Oct 30 Terry Haran
# Added station to filenames.

DATETIME=`date +\%Y\%m\%d_\%H\%M`
ID=/root/station

# get what AMIGOS unit this is
station=`cat $ID`

gpsdst=$(printf "/mnt/saved_images/%s_gpsdata_bakup_%s.gz" $station $DATETIME)
gzip /var/gpsdata -c > $gpsdst

altdst=$(printf "/mnt/saved_images/%s_altdata_bakup_%s.gz" $station $DATETIME)
gzip /var/altdata -c > $altdst

csidst=$(printf "/mnt/saved_images/%s_csidata_bakup_%s.gz" $station $DATETIME)
gzip /var/csidata -c > $csidst

wxtdst=$(printf "/mnt/saved_images/%s_wxtdata_bakup_%s.gz" $station $DATETIME)
gzip /var/wxtdata -c > $wxtdst

vltdst=$(printf "/mnt/saved_images/%s_vltdata_bakup_%s.gz" $station $DATETIME)
gzip /var/voltagedata -c > $vltdst

pwrdst=$(printf "/mnt/saved_images/%s_pwrdata_bakup_%s.gz" $station $DATETIME)
gzip /mnt/logs/repower_hist -c > $pwrdst

upldst=$(printf "/mnt/saved_images/%s_upldata_bakup_%s.gz" $station $DATETIME)
gzip /mnt/logs/upload_hist -c > $upldst

rm /var/gps
rm /var/gpsdata
rm /var/alt
rm /var/altdata
rm /var/wxt
rm /var/wxtdata
rm /var/csi
rm /var/csidata
rm /var/voltage
rm /var/voltagedata
rm /var/foo
rm /var/foodata

############ clear status bits just in case they get hung-up...
echo 0 > /var/IRD_status
echo 0 > /var/SBD_status
echo 0 > /var/GRS_status
