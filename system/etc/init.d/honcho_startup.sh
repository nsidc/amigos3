#!/usr/bin/env bash
source /media/mmcblk0p1/honcho/bin/set_paths.sh

mkdir -p /media/mmcblk0p1/logs

echo "Running amigo startup: $(date)" >> /media/mmcblk0p1/logs/startup.log

wdtick_1h.sh
supervise.sh &

cron start
