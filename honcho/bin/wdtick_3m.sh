#!/bin/bash

echo 1 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 0 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 1 > /sys/class/gpio/wdt_ctl/data 

logdir=/media/mmcblk0p1/logs
mkdir -p "${logdir}"
date >> "${logdir}/ticks_3m"
