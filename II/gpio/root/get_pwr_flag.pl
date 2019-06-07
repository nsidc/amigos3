#!/usr/bin/perl

$numArgs = $#ARGV + 1;
if ($numArgs != 2 || $ARGV[0] < 0 || $ARGV[0] > 2 || $ARGV[1] < 0 || $ARGV[1] > 7) {
	print "Usage: perl $PROGRAM_NAME byte_index bit_index\n";
	exit -1;
}

open (INDEX, ">/sys/class/gpio/pwr_ctl/index") || die;
flock(INDEX, 2) || die;
binmode( INDEX, ":unix" );
         
print INDEX $ARGV[0];
open (DATA, "/sys/class/gpio/pwr_ctl/data");
$value = hex(<DATA>);

$mask = 0x01 << $ARGV[1];

if ($value & $mask) {
	$ret = 1;
}
else {
	$ret = 0;
}

print "value read = " . sprintf("%02x", $value) . " or_mask = " . sprintf("%02x", $mask) . " ret = " . $ret . "\n";


close (DATA);
close (INDEX);

exit $ret;
