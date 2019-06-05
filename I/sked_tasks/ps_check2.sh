#!/bin/sh
#
# Wait for command PID to complete or kill after SECONDS seconds.
#
# syntax: 
#     ps_check2.sh PID SECONDS
#
# If job completes before SECONDS, exit code is 0.
# If SECONDS reached before job completes, exit code is 1.
# If PID not observed, exit code is -1.

PID=$1
SECONDS=$2

echo "ps_check2.sh $PID $SECONDS" | tee $PORT

CURRENT_TIME=`date +%s`
EXPIRATION_TIME=`expr $CURRENT_TIME + $SECONDS`

FOUND=0
while [ $CURRENT_TIME -le $EXPIRATION_TIME ]
do
    echo "Current time: $CURRENT_TIME  Target time: $EXPIRATION_TIME"

    if kill -0 $PID > /dev/null 2>&1 ; then
        echo "Process '$PID' is running"
        FOUND=1
    else
        if [[ $FOUND == 1 ]] ; then
            break
        fi
    fi

    sleep 10

    CURRENT_TIME=`date +%s`
done

if [[ $FOUND == 1 ]] ; then
    if kill -0 $PID > /dev/null 2>&1 ; then
        kill -s SIGTERM $PID
        sleep 1
        kill -0 $PID > /dev/null 2>&1 || kill -s SIGKILL $PID
        echo "Process '$PID' timed out and was killed"
        exit 1
    else
        echo "Process '$PID' completed"
        exit 0
    fi
else
    echo "Process '$PID' was not found"
    exit -1
fi
