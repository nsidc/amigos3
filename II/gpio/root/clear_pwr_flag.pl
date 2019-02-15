#!/usr/bin/perl

$numArgs = $#ARGV + 1;
if ($numArgs != 2 || $ARGV[0] < 0 || $ARGV[0] > 2 || $ARGV[1] < 0 || $ARGV[1] > 7) {
	print "Usage: perl $PROGRAM_NAME byte_index bit_index\n";
	exit -1;
}

# print "byte_index = " . $ARGV[0] . " bit_index = " . $ARGV[1] . "\n";

open (INDEX, ">/sys/class/gpio/pwr_ctl/index") || die;
flock(INDEX, 2) || die;
binmode( INDEX, ":unix" );
        
print INDEX $ARGV[0];
open (DATA, "+>/sys/class/gpio/pwr_ctl/data");
$value = hex(<DATA>);

$mask = 0x01 << $ARGV[1];
$mask = (~$mask) & 0xff;
# print "value read = " . sprintf("%02x", $value) . " and_mask = " . sprintf("%02x\n", $mask);

print INDEX $ARGV[0];
print DATA ($value & $mask);  

# print "data set = " . ($value & $mask) . "[dec]\n";
close (DATA);
close (INDEX);

exit 0;
