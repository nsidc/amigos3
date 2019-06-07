#!/bin/sh

# process foo to get the date of the data
# awk -F, 'NR == 1 {print $10}' gafa_3.txt 

# typical line
# Z 5 6 6 @ time 20 44 Volts = 12.28 Temp = 8.5 looper = 30 

# process latest_gps to get the last 24 hours of lat/lon on one line
awk '{for (x=1;x<NR;x+=1) {} } {print $11, $14 , $2"/"$3"/0"$4,  $7":"$8":00", $17 }' gafa_1.txt > gafa_cooked.txt

# process latest_gps to get the date of the data
# awk -F, '{for (x=1;x<NR;x+=1) {} } END {print $4$5,$6$7}' latest_gps > data/gps/latest/latest_position


