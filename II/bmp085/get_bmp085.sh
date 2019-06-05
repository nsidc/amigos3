#!/bin/sh

all_data=/var/tmp/bmp085
pressure=/var/tmp/bmp085_press
temperature=/var/tmp/bmp085_temp

#############

/mnt/bmp085/bmp085_press_temp > $all_data

awk ' $1 == "pressure:" {printf "%4.2f\n", $2} ' $all_data > $pressure 
awk ' $1 == "temperature:" {printf "%3.2f\n", $2} ' $all_data > $temperature 


############

