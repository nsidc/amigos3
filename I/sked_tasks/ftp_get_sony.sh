#!/bin/sh

# this script takes as many images as you like
# modified by RR 8/26/07 at Mona Vale for Wx7

#position1 is looking down the rest position to protect camera from sun
# test for overcoming ro sytstem

# 2009 Nov 10 Terry Haran
# Added saving Sony files 3-6.
#
# 2010 Oct 25 Terry Haran
# Changed /mnt/upload_images to /var/upload_images
#
# 2010 Oct 27 Terry Haran
# Changed postion syntax to $station$ImageSet$pos,
# e.g. amigos1b01
#
# 2010 Oct 30 Terry Haran
# Changed cd /var to cd $UPLOAD_IMAGES.
# Changed filenames.
# Fixed filenames.
#
# 2018 Dec 7 Bruce Wallin
# Changed to 3 picture 'c' batch always for firn aquifer project


ID=/root/station

# get what AMIGOS unit this is
station=`cat $ID`

# set the image set based on what time it is
hour=`date +\%H`
#if [ $hour -eq '14' ] ; then
#    ImageSet='a'
#    ImageCount=6
#else
#    ImageSet='b'
#    ImageCount=10
#fi
ImageSet='c'
ImageCount=4

UPLOAD_IMAGES="/var/upload_images"
IMAGESETFILE="$UPLOAD_IMAGES/ImageSet.txt"
IMAGECOUNTFILE="$UPLOAD_IMAGES/ImageCount.txt"
LOGFILE="$UPLOAD_IMAGES/sony.log"
DATETIME=`date +\%Y\%m\%d_\%H\%M`

echo $ImageSet >$IMAGESETFILE
echo $ImageCount >$IMAGECOUNTFILE

cd $UPLOAD_IMAGES

pos_safe=/mnt/sony/pos_safe

SONYFILE_txt="$UPLOAD_IMAGES/scratch"

SONYPICTUREURL=http://192.168.0.20:8082/oneshotimage.jpg
# PTZ speed to manual
SONYPTZURL_01=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101062403FF

echo "set auto-pan-tilt to off" >> $LOGFILE
wget $SONYPTZURL_01 -O $SONYFILE_txt
echo "Trying to move camera safe position" >> $LOGFILE
# $pos_safe
/mnt/sony/pos_safe
sleep 10

pos=1
while [ $pos -le $ImageCount ]
do
    SONYFILE=$(printf "%s%s%.2d_%s.jpg" $station $ImageSet $pos $DATETIME)

    command=$(printf "/mnt/sony/%s%s%.2d" $station $ImageSet $pos)
    echo "Trying to execute $command" >> $LOGFILE
    $command
    sleep 10
    wget $SONYPICTUREURL -O $SONYFILE
    sleep 1
    (( pos += 1 ))
done

echo "Trying to move camera safe position" >> $LOGFILE
# $pos_safe
/mnt/sony/pos_safe
sleep 3
exit 0
