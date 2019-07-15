#! /bin/bash

if [[ "$1" == "watchdog" ]]
then
    python /media/mmcblk0p1/amigos/cli.py $1 $2 &
else
    python /media/mmcblk0p1/amigos/cli.py $1 $2 $3
fi