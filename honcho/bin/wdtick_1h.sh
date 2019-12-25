#!/bin/bash

echo 3 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 2 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 3 > /sys/class/gpio/wdt_ctl/data 

logdir=/media/mmcblk0p1/logs
mkdir -p "${logdir}"
date >> "${logdir}/ticks_1h"
