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
# Corrected error on csidata and wxtdata RB June 3rd RR

# modified for Triton3 by RR @ RB on Feb 18th 2013
# modified for Wx8 @ RB on 1st August 2013, removed altgps and csi backups
# modified for Wx11 @ 10th St, 2016 to archive sbd_msgs and sleep, ie all in /mnt/logs
# added firn data archiving for KA1 by RR @ 10th St, 9/8/16
# removed data not relevant to AM2 by RR @ 10th St, 9/10/16

TIME=`date +%H%M%S`
DATE=`date +%m%d%y`
DATETIME=`date +%H%M_%m%d%y`
ID=/root/station
PORT=/dev/ttyS3
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

#####################################
# get what AMIGOS unit this is
station=`cat $ID`
#####################################

echo "" > $PORT
echo ">>>>> Executing $station, $caller, `date`" > $PORT
echo ">>>>> Executing $station, $caller, `date`" >> /mnt/logs/backup
#
# let other process like get_pcb finish
sleep 20
#
cd /var/tmp/
#
cp /var/tmp/gpsdata gpsdata_bak
gzip gpsdata_bak
mv gpsdata_bak.gz /mnt/saved_images/gpsdata_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/wxtdata wxtdata_bak
gzip wxtdata_bak
mv wxtdata_bak.gz /mnt/saved_images/wxtdata_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/pcbdata pcbdata_bak
gzip pcbdata_bak
mv pcbdata_bak.gz /mnt/saved_images/pcbdata_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/cr6data cr6data_bak                                            
gzip cr6data_bak                                                           
mv cr6data_bak.gz /mnt/saved_images/cr6data_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/imm imm_bak
gzip imm_bak
mv imm_bak.gz /mnt/saved_images/imm_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/immdata immdata_bak
gzip immdata_bak
mv immdata_bak.gz /mnt/saved_images/immdata_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/sbd_msgs sbd_msgs_bak
gzip sbd_msgs_bak
mv sbd_msgs_bak.gz /mnt/saved_images/sbd_msgs_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/upload_hist upload_hist_bak
gzip upload_hist_bak 
mv upload_hist_bak.gz /mnt/saved_images/upload_hist_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/repower_hist repower_hist_bak
gzip repower_hist_bak
mv repower_hist_bak.gz /mnt/saved_images/repower_hist_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/eth_status eth_status_bak
gzip eth_status_bak
mv eth_status_bak.gz /mnt/saved_images/eth_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/grs_status grs_status_bak
gzip grs_status_bak
mv grs_status_bak.gz /mnt/saved_images/grs_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/imm_status imm_status_bak
gzip imm_status_bak
mv imm_status_bak.gz /mnt/saved_images/imm_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/gps_status gps_status_bak
gzip gps_status_bak
mv gps_status_bak.gz /mnt/saved_images/gps_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/cr6_status cr6_status_bak                                            
gzip cr6_status_bak                                                           
mv cr6_status_bak.gz /mnt/saved_images/cr6_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/sleep sleep_status_bak
gzip sleep_status_bak
mv sleep_status_bak.gz /mnt/saved_images/sleep_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /mnt/logs/wxt_status wxt_status_bak
gzip wxt_status_bak
mv wxt_status_bak.gz /mnt/saved_images/wxt_status_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
cp /var/tmp/cr6data cr6data_bak                                            
gzip cr6data_bak                                                           
mv cr6data_bak.gz /mnt/saved_images/cr6data_bak_`date +\%H\%M_\%m\%d\%y`.gz
#
rm /var/tmp/gps*
rm /var/tmp/wxt*
rm /var/tmp/pcb*
rm /var/tmp/sbd*
rm /var/tmp/eth*
rm /var/tmp/repower*
rm /var/tmp/sleep*
rm /var/tmp/upload*
rm /var/tmp/immdata*
rm /var/tmp/cr6data*
rm /var/tmp/imm*
#
rm /mnt/logs/eth*
rm /mnt/logs/upload*
rm /mnt/logs/sleep*
rm /mnt/logs/wxt*
rm /mnt/logs/sbd*
rm /mnt/logs/gps*
rm /mnt/logs/grs*
rm /mnt/logs/cr6*
rm /mnt/logs/firn*
rm /mnt/logs/ftp_upload*
rm /mnt/logs/imm*
rm /mnt/logs/ps_check_results*
#
rm *_bak
#
# back to last dir
cd -

############ clear status bits for IRD and SBD just in case they get hung-up...
echo 0 > /var/tmp/IRD_status
echo 0 > /var/tmp/SBD_status
#
echo "<<<<< $station, $caller exit, `date`" > $PORT
echo "<<<<< $station, $caller exit, `date`" >> /mnt/logs/backup
#