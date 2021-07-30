#!/usr/bin/env bash
rm /media/mmcblk0p1/archive/honcho.tasks*
honcho seabird --run
honcho solar --run
honcho aquadopp --run
honcho crx --run
honcho gps --run
honcho weather --run
honcho dts --run
honcho camera --run
honcho tps --run
honcho sbd --run
honcho upload --run
honcho orders --run
cat /media/mmcblk0p1/archive/honcho.tasks*
