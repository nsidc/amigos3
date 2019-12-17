#!/usr/bin/env bash
/media/mmcblk0p1/honcho/bin/set_env.sh

honcho schedule --run >> /media/mmcblk0p1/logs/schedule.log 2>&1
