#!/usr/bin/env bash
source /media/mmcblk0p1/honcho/bin/set_env.sh

mkdir -p /media/mmcblk0p1/logs
honcho schedule --run >> /media/mmcblk0p1/logs/schedule.log 2>&1
