#!/bin/sh

ifconfig eth0 down
#/mnt/gpio/all_off
sleep 1
#/mnt/gpio/wdt_tick
# just to make sure
/mnt/gpio/wdt_tick
/usr/local/bin/pm_sleep +2min
/mnt/gpio/wdt_tick
