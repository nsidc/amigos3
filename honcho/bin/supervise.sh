#!/usr/bin/env bash
/media/mmcblk0p1/honcho/bin/set_env.sh

honcho supervise --run >> /media/mmcblk0p1/logs/supervisor.log 2>&1
