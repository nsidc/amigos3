#!/bin/sh

# INDEX 0

# note these are bit positions starting at 0

# INDEX 0
SBD_CTS=0
GRS=1
GPS=1
IMM=2
WXT=3
ETH_HUB=4
DTS=5
MOBO=6
##
V5_ENA=0
SERIAL_ENA=1
V5_SWITCH_ENA=3
# INDEX 1
SONY=2
IP6600=2
CR6=3
IRD=4

# echo "value of input = " $1
 
if [ $1 == 'sbd_cts_ON' ] ; then
index=0 ; bit=$SBD_CTS
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'sbd_cts_OFF' ] ; then
index=0 ; bit=$SBD_CTS
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

if [ $1 == 'grs_ON' ] ; then
index=0 ; bit=$GRS
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'grs_OFF' ] ; then
index=0 ; bit=$GRS
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

if [ $1 == 'gps_ON' ] ; then
index=0 ; bit=$GPS
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'gps_OFF' ] ; then
index=0 ; bit=$GPS
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
########

if [ $1 == 'imm_ON' ] ; then
index=0 ; bit=$IMM
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'imm_OFF' ] ; then
index=0 ; bit=$IMM
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

########
if [ $1 == 'wxt_ON' ] ; then
index=0 ; bit=$WXT
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'wxt_OFF' ] ; then
index=0 ; bit=$WXT
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

if [ $1 == 'hub_ON' ] ; then
index=0 ; bit=$ETH_HUB
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'hub_OFF' ] ; then
index=0 ; bit=$ETH_HUB
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
 
if [ $1 == 'dts_ON' ] ; then
index=0 ; bit=$DTS
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'dts_OFF' ] ; then
index=0 ; bit=$DTS
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
 
if [ $1 == 'mobo_ON' ] ; then
index=0 ; bit=$MOBO
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'mobo_OFF' ] ; then
index=0 ; bit=$MOBO
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
########
if [ $1 == 'ird_ON' ] ; then
index=0x1 ; bit=$IRD
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'ird_OFF' ] ; then
index=0x1 ; bit=$IRD
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
#########
if [ $1 == 'cr6_ON' ] ; then
index=0x1 ; bit=$CR6
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'cr6_OFF' ] ; then
index=0x1 ; bit=$CR6
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
#########

if [ $1 == 'ip6600_ON' ] ; then
index=0x1 ; bit=$IP6600
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'ip6600_OFF' ] ; then
index=0x1 ; bit=$IP6600
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

########
if [ $1 == 'V5_ENA_OFF' ] ; then
index=0x2 ; bit=$V5_ENA
/mnt/gpio/set_pwr_flag.pl $index $bit
fi
if [ $1 == 'V5_ENA_ON' ] ; then
index=0x2 ; bit=$V5_ENA
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi

if [ $1 == 'SERIAL_ENA_OFF' ] ; then
index=0x2 ; bit=$SERIAL_ENA
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
if [ $1 == 'SERIAL_ENA_ON' ] ; then
index=0x2 ; bit=$SERIAL_ENA
/mnt/gpio/set_pwr_flag.pl $index $bit
fi

if [ $1 == 'v5_switch_ena_OFF' ] ; then
index=0x2 ; bit=$V5_SWITCH_ENA
/mnt/gpio/clear_pwr_flag.pl $index $bit
fi
if [ $1 == 'v5_switch_ena_ON' ] ; then
index=0x2 ; bit=$V5_SWITCH_ENA
/mnt/gpio/set_pwr_flag.pl $index $bit
fi

# echo "value of index = " $index " and bit = " $bit  

