#!/bin/sh

# Genesis for Wx7 at Mona vale 7/21/07
# modified for amigos1 at RB 4/18/09
#
#
# HOST='192.220.74.204'this was thistle
# now # moved to polar66
# revised for mobotix D15 and Polar66 and EAGER, 4th April 2015, Crannell Dr, CO
#
PORT=/dev/ttyS3
HOST='192.249.115.17'
dummy_URL='ftp://192.249.115.17/dummy' 
dummy_tries_file='/mnt/sked_tasks/dummy_tries'
dummy_tries=8
dummy_local_file='/var/tmp/dummy'
WGET_seconds=60
IMGS="/mnt/saved_images/"
ID=/root/station
rm $dummy_local_file
#
call=`basename $0`
caller=`echo $call | tr [a-z] [A-Z]`

# get what AMIGOS unit this is and form account and passwd

######## check Iridium status first ########
IRD_status="/var/tmp/IRD_status"
SBD_status="/var/tmp/SBD_status"
#####################################
#
# get what AMIGOS unit this is
SBD=`cat $SBD_status`
IRD=`cat $IRD_status`
station=`cat $ID`
#
#####################################
echo ">>>>> Executing $caller @ `date`" > $PORT
echo "----- inside ftp_upload" > $PORT
sleep 1
#####################################
touch /var/tmp/$station
path=www/htdocs/$station
#
cd /var/tmp
#
mv mobo_left.jpg mobo_left_`date +\%H\%M_\%m\%d\%y`.jpg
mv mobo_right.jpg mobo_right_`date +\%H\%M_\%m\%d\%y`.jpg
# make a backup of all photos
cp mobo_*.jpg $IMGS
##
echo "----- webpath=$path" > $PORT
##
if [ -s $dummy_tries_file ] ; then
dummy_tries=`cat $dummy_tries_file`
fi
################### Script to keep trying to wget dummy before FTP begins, dummy must be non-zero
i=1
while [ ! -s $dummy_local_file ] && [ $i -le $dummy_tries ]
do 
/bin/ash /mnt/sked_tasks/ps_check_wget_tout $WGET_seconds &  
echo "----- in the wget loop" > $PORT
wget $dummy_URL -O $dummy_local_file
echo "----- times thru loop $i" > $PORT
i=`expr $i + 1`
done
#####################################
if [ ! -s $dummy_local_file ] ; then
echo "!!!!! unable to wget $dummy in $dummy_tries attempts" > $PORT
echo "!!!!! unable to receive remote dummy file" > $PORT
echo "!!!!! unable to wget after $i attempts, tries = $dummy_tries @ `date`" >> /mnt/logs/ftp_upload_status
echo 0 > /var/tmp/wget_completion_flag
/mnt/dial_out_devices_off
exit 0
else
echo "***** got wget after $i attempts, tries = $dummy_tries" > $PORT
echo "***** got wget after $i attempts, tries = $dummy_tries @ `date`" >> /mnt/logs/ftp_upload_status
echo "***** received remote dummy file ok" > $PORT
fi
#####################################
#
# make a backup of all photos
cp mobo_*.jpg $IMGS
#
ls -alrt mobo*.jpg | head -4 > last4_jpgs
awk '{print $9}' last4_jpgs > last4_pics
#
FILE1=`cat last4_pics | awk 'NR==1 {print $1;}'` 
FILE2=`cat last4_pics | awk 'NR==2 {print $1;}'`
FILE_SIZE1=`cat last4_jpgs | awk 'NR==1 {print $5;}'`
FILE_SIZE2=`cat last4_jpgs | awk 'NR==2 {print $5;}'`
#
echo "----- FILE1 = $FILE1, $FILE_SIZE1 bytes " > $PORT
echo "----- FILE2 = $FILE2, $FILE_SIZE2 bytes " > $PORT

station=`cat $ID`
FILE18=$station

echo "----- FILE18 = "$FILE18 > $PORT

echo "----- ps_check now launched" > $PORT
 
/mnt/sked_tasks/ps_check &

echo "----- FTP_UPLOAD begins" > $PORT
echo "----- FTP_UPLOAD begins @ " `date` >> /mnt/logs/ftp_upload_status

path=$station
#
ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd $path
passive
binary
lcd /var/tmp/
put $FILE1
put $FILE2
# put $FILE3
# put $FILE4
quit
END_SCRIPT
FTP_RETURN=$?
    echo "----- FTP_RETURN: $FTP_RETURN"
    echo "----- FTP_RETURN: $FTP_RETURN" > $PORT

if [ $FTP_RETURN == 0 ] ; then
echo "----- FTP_UPLOAD completed" > $PORT
echo "----- FTP_UPLOAD completed OK @ " `date` >> /mnt/logs/ftp_upload_status
else
echo "----- FTP_UPLOAD completed with error" > $PORT
echo "----- FTP_UPLOAD completed with error @ " `date` >> /mnt/logs/ftp_upload_status
fi
#
rm /var/tmp/*.jpg
rm /var/tmp/last_4*
#
echo "<<<<< $station, $caller exit @ `date`" > $PORT
#
exit 0
