#!/bin/sh

# built for Wx7 at Mona vale 7/21/07
# modified for amigos1 at RB 4/18/09
#
# 2009 Nov 5 Terry Haran
# Updated HOST, dummy, USER, and PASSWD for
# amigos1 account on sidads.colorado.edu,
# and added "cd incoming" to ftp commands.
#
# 2009 Nov 8 Terry Haran
# Updated dummy for amigos wget ftp access.
# Added check for existence of dummy file after dummy_tries attempts
# and exit if dummy file does not exist.
#
# 2009 Nov 9 Terry Haran
# Added dummy_tries_file and
# added test for dummy_tries gt 0.
#
# 2009 Nov 10 Terry Haran
# Added ftp of sony pictures 3-6.
#
# 2009 Nov 11 Terry Haran
# Got rid of ftp of sony scratch file.
#
# 2009 Nov 16 Terry Haran
# Merged with Ronald Ross' amigos2-11072009 code.
#
# 2009 Nov 17 Terry Haran
# Commented out the exit when dummy_tries is exceeded.
#
# added NSIDC FTP sidads.colorado.edu by RR at RB 2nd Nov 2009
#
# 2010/01/11 Terry Haran
# Changed weather to wxt.
# Added csi.
# Removed extraneous NC comments.
# Added back put of $station file.
# Removed extraneous semicolons.
#
# 2010/01/12 Terry Haran
# Added alt and altdata.
#
# 2010/03/14 Terry Haran
# Changed thumbnail image size from 240 to 320 across.
#
# 2010 Oct 25 Terry Haran
# Changed /mnt/upload_images to /var/upload_images.
# Changed copying backups to getting the last 7 from /mnt/saved_images.
# Changed date/time format.
#
# 2010 Oct 30 Terry Haran
# Changed echoing to terminal to echoing to logfile.
# Changed filenames.
# Fixed copying files to saved_images.
#
# 2010 Nov 23 Terry Haran
# Only ftp backup files if ImageCount greater than 6.
# Replaced UPLOAD_IMAGES with UPLOADIMAGES.
# Replaced SAVED_IMAGES with SAVEDIMAGES.
#
# 2015 Sep 1 Terry Haran
# Replaced sidads.colorado.edu with restricted.ftp.nsidc.org for dialouts
#          128.138.135.20           128.138.135.165     
#
# 2018 Dec 7 Bruce Wallin
# Added handling for ImageCount = 4 (firnaqua project)‰
# Removed passwords to let .netrc do the login
# Removed if block around ftp to simplify

UPLOADIMAGES="/var/upload_images"
IMAGESETFILE="$UPLOADIMAGES/ImageSet.txt"
IMAGECOUNTFILE="$UPLOADIMAGES/ImageCount.txt"
LOGFILE="$UPLOADIMAGES/sony.log"
SAVEDIMAGES="/mnt/saved_images"
DATETIME=`date +\%Y\%m\%d_\%H\%M`
YEAR=`date +\%Y`

# now sidads
dummy_tries_file='/mnt/sked_tasks/dummy_tries'
dummy_tries=5
ID=/root/station

# get what AMIGOS unit this is and form account and passwd
station=`cat $ID`

# run the IPA getter on tzo
# /mnt/sked_tasks/ip-up.sh

cd $UPLOADIMAGES
touch $station

if [ -s $dummy_tries_file ] ; then
dummy_tries=`cat $dummy_tries_file`
fi

################### Script to keep trying to wget dummy before FTP begins, dummy must be non-zero
if [ $dummy_tries -gt 0 ] ; then
i=1
while [ ! -s dummy ] && [ $i -le $dummy_tries ]
do   
echo "in the wget loop" >> $LOGFILE
wget $dummy -O dummy
echo "times thru loop $i" >> $LOGFILE
i=`expr $i + 1`
/mnt/utils/chkr
done
if [ ! -s dummy ] ; then
echo "unable to wget $dummy in $dummy_tries attempts" >> $LOGFILE
# exit 1
else
echo "out of wget loop after $i attempts" >> $LOGFILE
fi
fi
##################
# instead try wget four
# wget $dummy -O dummy
# wget $dummy -O dummy
##################

ImageSet=`cat $IMAGESETFILE`
ImageCount=`cat $IMAGECOUNTFILE`

BackupCount=7
if [ $ImageCount -gt 6 ] ; then
    BackupCount=0
fi

# make a backup of all photos
command=$(printf "cp %s*.jpg %s" $station $SAVEDIMAGES)
echo "Trying to execute $command" >> $LOGFILE
`$command`

# create thumbnails of jpegs with prefix tn_.jpg
command=$(printf "/mnt/thumbs/jpgtn -f -s 320 %s*.jpg" $station)
echo "Trying to execute $command" >> $LOGFILE
`$command`

ls -1rt tn*.jpg | head -$ImageCount > last_pics

# create a list of the most recent 7 backup files
cd $SAVEDIMAGES
ls -1rt *bakup_$YEAR*.gz | tail -$BackupCount >"$UPLOADIMAGES/last7_baks"
cd $UPLOADIMAGES

FILE1=`cat last_pics | awk 'NR==1 {print $1;}'` 
FILE2=`cat last_pics | awk 'NR==2 {print $1;}'`
FILE3=`cat last_pics | awk 'NR==3 {print $1;}'`
FILE4=`cat last_pics | awk 'NR==4 {print $1;}'`
FILE5=`cat last_pics | awk 'NR==5 {print $1;}'`
FILE6=`cat last_pics | awk 'NR==6 {print $1;}'`
FILE7=`cat last_pics | awk 'NR==7 {print $1;}'`
FILE8=`cat last_pics | awk 'NR==8 {print $1;}'`
FILE9=`cat last_pics | awk 'NR==9 {print $1;}'`
FILE10=`cat last_pics | awk 'NR==10 {print $1;}'`

FILE11=`cat last7_baks | awk 'NR==1 {print $1;}'`
FILE12=`cat last7_baks | awk 'NR==2 {print $1;}'`
FILE13=`cat last7_baks | awk 'NR==3 {print $1;}'`
FILE14=`cat last7_baks | awk 'NR==4 {print $1;}'`
FILE15=`cat last7_baks | awk 'NR==5 {print $1;}'`
FILE16=`cat last7_baks | awk 'NR==6 {print $1;}'`
FILE17=`cat last7_baks | awk 'NR==7 {print $1;}'`

FILE18=$station

/mnt/sked_tasks/ps_check &

ftp -v restricted_ftp >> $LOGFILE <<END_SCRIPT_4
cd incoming
passive
binary
lcd $UPLOADIMAGES
put $FILE1
put $FILE2
put $FILE3‰

lcd $SAVEDIMAGES
put $FILE11
put $FILE12
put $FILE13
put $FILE14
put $FILE15
put $FILE16
put $FILE17

lcd $UPLOADIMAGES
put $FILE18
quit
END_SCRIPT_4
