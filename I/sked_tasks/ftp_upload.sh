#!/bin/sh

local_dummy='/mnt/dummy'

# run the IPA getter on tzo
/mnt/sked_tasks/ip-up.sh

cd /mnt/upload_images/
cp /mnt/gps/gpstime .
cp /mnt/gps/gpsdata .
gzip gpsdata
cp /var/voltage .
cp /var/voltagedata .
gzip voltagedata

cp /mnt/radar/radar .
cp /mnt/radar/radardata .
gzip radardata

cp /var/repower_hist .
gzip repower_hist
cp /mnt/logs/upload_hist .
gzip upload_hist
cp /var/ip.html .

# check to see if GPS and Voltage backup files exist and if so copy them to here and upload
if [ -f /mnt/bak/gpsdata_bak ] ; then
cp /mnt/bak/gpsdata_bak .
gzip gpsdata_bak 
rm /mnt/bak/gpsdata_bak ;
fi

if [ -f /mnt/bak/voltagedata_bak ] ; then
cp /mnt/bak/voltagedata_bak . ;
gzip voltagedata_bak
rm /mnt/bak/voltagedata_bak ;
fi

if [ -f /mnt/bak/radardata_bak ] ; then
cp /mnt/bak/radardata_bak . ;
gzip radardata_bak
rm /mnt/bak/radardata_bak ;
fi

mv Sony_01.jpg ./Sony_01_`date +\%H\%M_\%m\%d\%y`.jpg
mv Sony_02.jpg ./Sony_02_`date +\%H\%M_\%m\%d\%y`.jpg
mv Sony_03.jpg ./Sony_03_`date +\%H\%M_\%m\%d\%y`.jpg
mv NC.jpg ./NC_`date +\%H\%M_\%m\%d\%y`.jpg

# make a backup of all photos
cp Sony_*.jpg /mnt/saved_images/
cp NC_*.jpg /mnt/saved_images/

# create thumbnails of jpegs with prefix tn_.jpg
# /mnt/thumbs/jpgtn -f -s 240 Sony*.jpg
# /mnt/thumbs/jpgtn -f -s 240 NC*.jpg

# ls -lrt tn*.jpg | head -4 > last4_jpgs
ls -lrt *.jpg | head -4 > last4_jpgs
awk '{print $9}' last4_jpgs > last4_pics
FILE1=`cat last4_pics | awk 'NR==1 {print $1;}'` 
FILE2=`cat last4_pics | awk 'NR==2 {print $1;}'`
FILE3=`cat last4_pics | awk 'NR==3 {print $1;}'`
FILE4=`cat last4_pics | awk 'NR==4 {print $1;}'`

FILE5=gpsdata.gz
FILE6=gpstime
FILE7=voltage
FILE8=voltagedata.gz
FILE9=radardata.gz
FILE10=repower_hist.gz
FILE11=upload_hist.gz
FILE12=gpsdata_bak.gz
FILE13=voltagedata_bak.gz
FILE14=radardata_bak.gz
FILE15=ip.html

/mnt/sked_tasks/ps_check &

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd /www/htdocs/amigos1/
passive
binary
lcd /mnt/upload_images
put $FILE1
put $FILE2
put $FILE3
put $FILE4
ascii
put $FILE5
put $FILE6
put $FILE7
put $FILE8
put $FILE9
put $FILE10
put $FILE11
put $FILE12
put $FILE13
put $FILE14
put $FILE15
quit
END_SCRIPT
exit 0
