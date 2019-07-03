#! /bin/bash
AMIGOS_DIR=/media/mmcblk0p1
if [[ "$1" == "watchdog" ]]
then
    cd $AMIGOS_DIR && python -m amigos.cli $1 $2 &
else
    cd $AMIGOS_DIR && python -m amigos.cli $1 $2 $3
fi
