#!/bin/sh
ID=/root/station
index_file=/mnt/html/index.html


# SET for correct AMIGOS number!!!!!!!!!!!!!
# get what AMIGOS unit this is
station=`cat $ID`

x=$(cat /mnt/html/part3)

if [ $station == 'amigos1' ] ; then amigos='A1' ; fi
if [ $station == 'amigos2' ] ; then amigos='A2' ; fi
if [ $station == 'amigos3' ] ; then amigos='A3' ; fi
if [ $station == 'amigos4' ] ; then amigos='A4' ; fi
if [ $station == 'amigos5' ] ; then amigos='A5' ; fi
if [ $station == 'amigos6' ] ; then amigos='A6' ; fi

cat /mnt/html/part1 > $index_file
echo "<title>" $station "hello page</title>" >> $index_file
cat /mnt/html/part2 >> $index_file
echo $x $amigos "</a><br>" >> $index_file
cat /mnt/html/part4 >> $index_file

