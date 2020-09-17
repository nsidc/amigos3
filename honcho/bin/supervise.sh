#!/usr/bin/env bash
source /media/mmcblk0p1/honcho/bin/set_env.sh

mkdir -p /media/mmcblk0p1/logs
honcho supervise --run >> /media/mmcblk0p1/logs/supervisor.log 2>&1
