#!/bin/sh

cd /var/tmp

tail -200 latest1.ddf > tt
head -50 tt > tt1
tail -150 tt > mid
head -50 mid > tt2
tail -100 mid > end
head -50 end > tt3
tail -50 end > tt4

tail -200 latest3.ddf > 3tt
head -50 tt > 3tt1
tail -150 tt > 3mid
head -50 mid > 3tt2
tail -100 mid > 3end
head -50 end > 3tt3
tail -50 end > 3tt4


