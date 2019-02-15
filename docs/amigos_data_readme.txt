AMIGOS data files.
Terry Haran now retired and replaced by Bruce Wallin
wallinb@nsidc.org
2017/12/28

This document describes how you can browse LARISSA AMIGOS data
stored in various directories on nsidc-tharan and describes the
content of those directories.

First ssh to your account on nsidc-tharan. Then, once you are logged in,
execute the following commands:

setenv HOME /home/tharan
cd $HOME
ssh-agent /usr/bin/csh
source .login
source .cshrc

These commands will change your $shell to /bin/tcsh and set up the
environment variables and aliases you need to navigate the AMIGOS data
files. When you are done, type the exit command twice: the first will
exit you from /bin/tcsh, and the second will exit your login to
nsidc-tharan.

The first thing to understand about AMIGOS data files is that there
are two different data sets: a Near Real-Time (NRT) data stream and
an Archive (ARCH) data set. NRT data are received at NSIDC via the
Iridium modem on each AMIGOS. ARCH data are stored on the Compact
Flash (CF) memory device on each AMIGOS that also holds most of the
AMIGOS firmware. On AMIGOS-6 (Cape Disappointment) there is an
additional Secure Digital (SD) memory device that stores high
resolution images acquired by the Nikon camera. These ARCH data sets
are not received at NSIDC until the memory devices are physically
retrieved from the AMIGOS units in the field.

NRT Data

NRT data are further subdivided into two two separate data streams:
a NRT Single Burst Data (SBD) stream and Dial-Out Data (DOD) stream.

NRT SBD

The NRT SBD stream is updated continuously by the AMIGOS units that
are still operational. Currently, the only such unit is AMIGOS-1 (Matienzo).
AMIGOS-2 (NSIDC roof) hasn't returned data since 2017/10/26.
and is now damaged and stored in the NSIDC radar lab.
AMIGOS-3 (Flask Glacier) hasn't returned data since 2015-03-08.
AMIGOS-4 (Scar Inlet) hasn't returned data since since 2017/08/23.
AMIGOS-5 (Site Beta) hasn't returned data since 2010-07-20.
AMIGOS-6 (Cape Disappointmnet) hasn't returned data since 2017/12/02,
when it was removed from Cape Disappintment, and is currently enroute from
Rothera Base to NSIDC Bouldervia Punta Arenas.

The NRT SBD stream consists of ASCII text files stored in:

ftp://sidads.colorado.edu/pub/incoming/wallinb/amigos/

The files in this directory are also available in
directory /disks/sidads_incoming/wallinb/amigos

The data for the current year from the operational AMIGOS units are
in files amigosN_sbd.txt as described in:

ftp://sidads.colorado.edu/pub/incoming/wallinb/amigos/amigos_wxt_readme.txt

Data for previous years (YYYY) are in files amigosN_sbd_YYYY.txt. The
/disks/sidads_incoming/wallinb/amigos directory contents have been intermittently
backed up to:
/disks/tharan/data2/tharan/larissa/amigos/Downloads
with the most recent backup in subdirectory from_sidads_2017-12-21

NRT DOD

NOTE: The NRT DOD stream described below stopped working due to some still unresolved
change in the USAP Iridium system as of 2016/10/31.

The NRT DOD stream consists of JPEG browse images, various gzipped
(8.gz) ascii housekeeping data files, and (for AMIGOS-1, AMIGOS-2,
AMIGOS-3, and AMIGOS-4) tarred and gzipped (*.tgz) ascii high resolution Topcon GPS data
files in TPS format.

All NRT DOD data files can be found in directories accessible from nsidc-tharan
having the form /disks/restricted_ftp/amigosN/incoming/YYYYMM where:
  N is AMIGOS number 1-6.
  YYYY is the year 2010-2017.
  MM is the month 01-12.
The one exception is amigos5, whose only NRT DOD housekeeping data can be found in
/disks/tharan/data2/tharan/larissa/amigos/Downloads/from_sidads_2010-08-16/amigos5.

AMIGOS source code gzipped tar (*.tgz) files can be found in
/disks/tharan/data/tharan/larissa/amigos/tarfiles.

The git repository for amigos code can be found in
https://bitbucket.org/nsidc/tmh_larissa.git.
