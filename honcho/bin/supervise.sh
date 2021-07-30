#!/usr/bin/env bash
source /media/mmcblk0p1/honcho/bin/set_env.sh

mkdir -p /media/mmcblk0p1/logs
# Commented so that honcho schedule does not run on startup/cron etc... during testing
# honcho supervise --run >> /media/mmcblk0p1/logs/supervisor.log 2>&1
