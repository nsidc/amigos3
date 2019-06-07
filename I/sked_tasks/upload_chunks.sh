#!/bin/sh
# syntax: ftp_upload_chunks.sh FILELIST
#    Will split each file into chunks and upload one at a time
# Notes:
#    Uses hostnames from '/etc/hosts'
#    Uses login details and ftp macros from '/.netrc'

FILELIST=$1

PORT=/dev/ttyS0

# HOST='laptop'  # For local testing
HOST='restricted_ftp'  # In the field

FTP_MINUTES=30
FTP_LOGFILE=/mnt/logs/ftp_chunk.log
FTP_COMMAND='ftp'
FTP_ARGS="-v $HOST"

CHUNK_SIZE=1000  # bytes
CHUNK_TIMEOUT=30  # seconds

if [ ! -s $FILELIST ] ; then
    echo "No files in $FILELIST" | tee $PORT
    exit 0
fi

######## check battery first ########

BATTERY_LOW=`cat /var/voltage_status`

#####################################

if [ $BATTERY_LOW == 1 ] ; then
    echo "Battery Voltage too LOW for GRS!! " $Input_voltage "mVolts @ " `date` | tee $PORT
    exit 1
fi

######## check Iridium status ########

IRD_status="/var/IRD_status"
SBD_status="/var/SBD_status"

SBD=`cat $SBD_status`
IRD=`cat $IRD_status`

#####################################

while [ $SBD == 1 ]
do
    echo "SBD in use, waiting " `date` | tee $PORT
    sleep 21
    SBD=`cat $SBD_status`
done

echo "SBD is now free " `date` | tee $PORT

#####################################

while [ $IRD == 1 ]
do
    echo "Iridium in use, waiting " `date` | tee $PORT
    sleep 21
    IRD=`cat $IRD_status`
done
    
echo "Iridium is now free " `date` | tee $PORT

#####################################
echo "1" > $IRD_status
#####################################

/mnt/gpio/ftp_devices_on

cd /mnt/saved_images

rm $FTP_LOGFILE

CURRENT_TIME=`date +%s`
TARGET_TIME=`expr $CURRENT_TIME + 60 \* $FTP_MINUTES`
while [ -s $FILELIST ] && [ $CURRENT_TIME -lt $TARGET_TIME ]
do
    FILENAME=`head -1 $FILELIST`
    echo "Attempting to upload '$FILENAME' in chunks" | tee $PORT

    # Split into chunks if not done already
    CHUNK_PREFIX="${FILENAME}.chunk_"
    CHUNK_FILELIST="${CHUNK_PREFIX}list.txt"
    if [ ! -s $CHUNK_FILELIST ] ; then
        echo "Splitting '$FILENAME' into $CHUNK_SIZE byte chunks" | tee $PORT
        split -b $CHUNK_SIZE $FILENAME $CHUNK_PREFIX

        # Add chunks including chunk filelist in manifest to upload
        echo "$CHUNK_FILELIST" > $CHUNK_FILELIST
        ls ${CHUNK_PREFIX}* >> $CHUNK_FILELIST
    else
        echo "'$CHUNK_FILELIST' exists. Skipping splitting operation" | tee $PORT
    fi

    # Upload chunks in chunklist
    CURRENT_TIME=`date +%s`
    while [ -s $CHUNK_FILELIST ] && [ $CURRENT_TIME -lt $TARGET_TIME ]
    do
        # Attempt to FTP file with timeout
        CHUNK_FILENAME=`head -1 $CHUNK_FILELIST`
        echo "Executing $FTP_COMMAND $FTP_ARGS $CHUNK_FILENAME with timeout of $CHUNK_TIMEOUT" | tee $PORT

        echo "\$ uploadfile $CHUNK_FILENAME" | \
            $FTP_COMMAND $FTP_ARGS >> $FTP_LOGFILE &
        FTP_PID=$!

        /mnt/sked_tasks/ps_check2.sh $FTP_PID $CHUNK_TIMEOUT
        PS_CHECK_STATUS=$?

        # Check if upload successful, if so remove from chunk list
        if [ $PS_CHECK_STATUS == 0 ] ; then
            FTP_SUCCESS_MSG="226-File successfully transferred"
            if fgrep "$FTP_SUCCESS_MSG" $FTP_LOGFILE ;then
                echo "Upload OK. Removing $CHUNK_FILENAME from $CHUNK_FILELIST" | tee $PORT
                sed -i "/$CHUNK_FILENAME/d" $CHUNK_FILELIST
            else
                echo "Upload Error: " | cat - $FTP_LOGFILE | tee $PORT
            fi
        elif [ $PS_CHECK_STATUS == 1 ] ; then
            echo "FTP upload timed out and was terminated"
        elif [ $PS_CHECK_STATUS == -1 ] ; then
            echo "FTP upload ended before ps_check could observe it. Suspicious..."
        fi

        CURRENT_TIME=`date +%s`
    done

    # Check if all chunks uploaded successfully
    if [ ! -s $CHUNK_FILELIST ] ; then
        echo "All chunks uploaded. Removing $FILENAME from $FILELIST" | tee $PORT
        sed -i "/$FILENAME/d" $FILELIST
        rm ${CHUNK_PREFIX}*
    else
        echo "Incomplete upload of $FILENAME" | tee $PORT
    fi

    CURRENT_TIME=`date +%s`
done

if [ ! -s $FILELIST ] ; then
    echo "No more files to ftp in $FILELIST" | tee $PORT
fi

if [ $CURRENT_TIME -ge $TARGET_TIME ] ; then
    echo "$FTP_MINUTES minute total timeout exceeded" | tee $PORT
fi
    
#########################
# clear the busy flags
echo "0" > $IRD_status
    
/mnt/gpio/dial_out_devices_off
    
echo "End of upload_chunks.sh" | tee $PORT
