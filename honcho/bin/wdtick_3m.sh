#!/bin/sh

echo 1 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 0 > /sys/class/gpio/wdt_ctl/data
sleep 1
echo 1 > /sys/class/gpio/wdt_ctl/data 
