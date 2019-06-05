#!/bin/sh

ID=/root/station

# get what AMIGOS unit this is
station=`cat $ID`

ImageSet='b'
ImageCount=10

UPLOADIMAGES="/var/upload_images"
SAVEDIMAGES="/mnt/saved_images"
IMAGESETFILE="$UPLOADIMAGES/ImageSet.txt"
IMAGECOUNTFILE="$UPLOADIMAGES/ImageCount.txt"
LOGFILE="$UPLOADIMAGES/sony.log"
DATETIME=`date +\%Y\%m\%d_\%H\%M`

`rm -fr $UPLOADIMAGES`
`mkdir $UPLOADIMAGES`

echo $ImageSet >$IMAGESETFILE
echo $ImageCount >$IMAGECOUNTFILE

cd $UPLOADIMAGES

pos_safe=/mnt/sony/pos_safe

SONYFILE_txt="$UPLOADIMAGES/scratch"

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
    `mv $SONYFILE $SAVEDIMAGES`
    (( pos += 1 ))
done

echo "Trying to move camera safe position" >> $LOGFILE
# $pos_safe
/mnt/sony/pos_safe
sleep 3
exit 0
