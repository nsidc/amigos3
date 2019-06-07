AMIGOS image files.
Terry Haran
tharan@nsidc.org
2016/10/18

Directory is:

ftp://sidads.colorado.edu/pub/incoming/tharan/amigos/amigosN_images/

Thumbnail filenames are of the form: tn_amigosNTII_YYYYMMDD_HHMM.jpg
  where
    N is amigos number 1-6.
      amigos1 - Matienzo Base         64d 58.57' S
                                      60d 04.19' W =
                                      -64.9762 -60.0699    30 m asl
      amigos2 - NSIDC roof in Boulder 40d  0.75' N
                                     105d 15.18' W =
                                      40.0125 -105.2530  1624 m asl
                amigos2 is currently stored in the NSIDC lab.
      amigos3 - Lower Flask Glacer    65d 46.63' S
                                      62d 14.15' W =
                                      -65.7771 -62.6859   406 m asl
                amigos3 has not been heard from since 2015/03/08.
      amigos4 - Scar Inlet Ice Shelf  65d 46.52' S
                                      61d 55.06' W =
                                      -65.7753 -61.9177    46 m asl 
      amigos6 - Cape Disappointment   65d 33.98' S
                                      61d 44.88' W =
                                      -65.5664 -61.7480   234 m asl

    TII is Image Type and Image Number:
      a01-a06: Sony 320x240 housekeeping images acquired at 14:00:
        amigos1, amigos3 & amigos4:
          a01: WXT520 weather sensor & accumulation pole.
          a02: straight down view of enclosure and lower solar panel.
	  a03: close-up of upward-looking solar sensor and mirror.
          a04: zoomed view north.
	  a05: zoomed view:
               amigos1: west southwest: Dalman Nunatak
               amigos3: east southeast: Spouter Peak.
               amigos4: east
	  a06: zoomed view:
               amigos3 southeast: Bildad Peak.
	       amigos4 west southwest: Flask Glacier.
        amigos6:
          a01: southwest rock anchors and accumulation pole.
          a02: straight down view of Nikon high-res camera.
	  a03: WXT520 weather sensor.
	  a04: close-up of upward-looking solar sensor and mirror.
	  a05: northern rock anchor and bottom two solar panels.
	  a06: southeast rock anchors.

      b01-b10:
          Sony 320x240 images 360 degree images acquired at times
	    other than 14:00.
          amigos1, amigos3 & amigos4:
            b01-b10 360 degree images, approx 35 deg spacing clockwise:
	    b01 view is south except on amigos1 where it is southeast.
          amigos6:
            b01 view is southeast.
	    b02 view is southwest.
	    b03 view is zoomed on calving front southeast.
	    b04-b10 each image is panning right (west).
            b10 view is zoomed on calving front southwest.

      c01-c04: Nikon 968x648 images:
          amigos6 view of Scar Inlet embayment and ice shelf calving front:
            c01 view is east southeast
            c02 view is south southeast
            c03 view is south southwest
            c04 view is west southwest
      NOTE: c01-c04 images from amigos6 have not been received
            since 2016/09/10 due to an apparent problem with
            the interface between the Nikon camera and Triton single board
            computer.

    YYYYMMDD - UTC year month day hour minute of image acquisition.

    amigosaII* files are posted at 20 minutes past their acquistion time.
    amigosbII* files are posted at 20 minutes past their acquistion time.
    amigoscII* files are posted at 40 minutes past their acquistion time.

amigos3 SBD data and images have not been posted since 2015/03/08.

amigos6 SBD data are still being posted, but high resolution Nikon images
have not been posted since 2016/09/10 due to an apparent problem with
the interface between the Nikon camera and Triton single board computer.

Understanding and Modifying the Current Camera Positions on AMIGOS-1

NOTE: The a?? and b?? camera positions described above and in the following
instructions assume that the amigos1b01_YYYYMMDD_1501.jpg position is due south.

1) All 640x480 images are stored in directory /mnt/saved_images and have
filenames of the form: amigos1TII_YYYYMMDD_HHMM.jpg as described above.
2016/08/12 appears to have been a sunny day, so copy all of those 640x48 images
to the laptop using ftp:

ftp 192.168.0.80
Name: root
Password: Enter the password
prompt
binary
cd /mnt/saved_images
mget amigos1*20160812*jpg
quit

2) The previous step should have retrieved the following files:

amigos1a01_20160812_1401.jpg
amigos1a02_20160812_1401.jpg
amigos1a03_20160812_1401.jpg
amigos1a04_20160812_1401.jpg
amigos1a05_20160812_1401.jpg
amigos1a06_20160812_1401.jpg
amigos1b01_20160812_1501.jpg
amigos1b02_20160812_1501.jpg
amigos1b03_20160812_1501.jpg
amigos1b04_20160812_1501.jpg
amigos1b05_20160812_1501.jpg
amigos1b06_20160812_1501.jpg
amigos1b07_20160812_1501.jpg
amigos1b08_20160812_1501.jpg
amigos1b09_20160812_1501.jpg
amigos1b10_20160812_1501.jpg

3) Look at each of the 6 amigos1a??_20160812_1401.jpg images
and the 10 amigos1b??_20160812_1501.jpg images and compare them
to the amigos3 a01-a06 and b01-b10 descriptions above. The initial
amigos1??? and the "current" amigos3??? camera positions are very similar
(although AMIGOS-3 is currently not working).

4) From the laptop:

telnet 192.168.0.80

5) Disable all crontab non-essential crontab entries:

crontab -e
Down-arrow
Down-arrow
dd
dd
dd
...

Keep pressing dd until only the following entries remain in crontab:

*/1 * * * * /mnt/gpio/wdt_tick
*/1 * * * * /mnt/sked/voltage_checker.sh

Then:

:wg

6) /mnt/gpio/dial_out_devices_on

After a minute or so, you should see:

SIOCADDRT: File exists
bash-2.05b#

7) On your laptop, open a browser, and go to the AMIGOS-1 Welcome Page:

192.168.0.80

Username: triton
Password: Enter the password

8) Select PTZ (which stands for Pan, Tilt, Zoom)

9) Select Java Applet Viewer

10) You should see an upside-down live image in the SONY window that
updates at 1 frame per second. We'll need to set Image flip On, change
the camera postions, and then set Image flip to Off when we're
done. For now, click "Setting", and login to the camera with username
"sony" and the same password as usual. This should create the "Setting
menu" popup window.

11) In the "Setting menu", Click "Camera". This changes the popup to 
"Camera setting".

12) Select "Image flip On", click the adjacent "Apply" button, and 
then close the "Camera setting" popup. You should now see a rightside-up image
in the "SONY" live image window.

13) Back in the telnet window:

cd /mnt/sony
ls -l amigos1???

You should see something like:

amigos1a01
amigos1a02
amigos1a03
amigos1a04
amigos1a05
amigos1a06
amigos1b01
amigos1b02
amigos1b03
amigos1b04
amigos1b05
amigos1b06
amigos1b07
amigos1b08
amigos1b09
amigos1b10

Each of these files is an executable shell script that sets the pan, tilt,
and zoom for a particular camera position. You can simply run a particular
script, for example the amigos1a01 script, by typing:

./amigos1a01

You will see the camera move and the SONY live image change to one that should
closely match the amigos1a01_20160812_1401.jpg that you downloaded in
step 1 above. Try verifying that amigos1b01 points the camera due south,
and that amigos1a06 points the camera southeast, and that the resulting
live images match the corresponding downloaded images.\

14) In the telnet window, type:

./amigos1a01

This is the first image that is acquired at 14:00 UTC. Let's say we want
to change this image to point to something that includes more of the
battery box that is just visible at the bottom of the frame. Click "Control".
You should now see an additional set of arrow buttons, a "WIDE" button, and
a "TELE" button. Click the up-arrow button 3 times. This causes the image to
sroll upward, allowing you to see more of the battery box. Try clicking the
other arrow buttons to see how they work. Note that if you click "wIDE",
nothing happens because the amigos1a01 view is zoomed back as far as is
possible, but clicking "TELE" zooms in. You can also zoom in or out using
the "ruler" underneath the image. You can restore the amigos1a01 camera
position by going back to the telnet image and typing:

 ./amigos1a01

15) In addition to the amigos1??? scripts, the /mnt/sony directory contains
additional scripts that let you create or modify camera position scripts.
The most important of these is the "make_pos" script. Try modifying the
amigos1a01 image as we did in the previous step until you have a camera
position that you want to save. Then type:

./make_pos

You get:

Enter number for new position

Type:

1

You get:

Connecting to 192.168.0.20[192.168.0.20]:8082
curr_pos             100% |********************************************************************|    22       00:00 ETA
Connecting to 192.168.0.20[192.168.0.20]:8082
curr_zoom            100% |********************************************************************|    14       00:00 ETA
0 0 0 0
f e e c 0 1 7 8
 New file is called pos1 

16) There should now be a new file in /mnt/sony called pos1. If you want
that file to replace the current amigos1a01 position, you could type the
following:

mv amigos1a01 amigos1a01.sav
mv pos1 amigos1a01

So typing ./amigos1a01 should now move the camera to the new amigos1a01
position.

17) You could now do the same procedure for the amigos1a02, amigos1a03
... and amigosb01, amigosb02, etc.  positions. Note that these
amigos1a?? positions are "hard-coded" to consist of 6 positions that
are always acquired at 14:00 UTC. The amigos1b??  positions are
hard-coded to consist of 10 images that are acquired at at times other
than 14:00. If you need these hard-coded values changed, let me know
what would better suit your needs, and I'll try implementing them here
with our test system in Boulder, and then sending you the modified
code.

18) Once you have a modified set of amigos1a?? and amigos1b?? position
scripts that you like, be sure to set the Image flip setting to Off:

Click "Setting", then click "Camera", then select Image flip Off, then
click the adjacent "Apply" button.

The SONY live image should now look upside=down, which is necessary for
the acquired amigos1a?? and amigos1b?? images to look rightside up.

19) Reboot the system which will restore the crontab by typing:

shutdown -r now

20) Once the system comes back up, verify that the date/time looks correct,
and fix it if it is wrong. For example, I had to do the following:

bash-2.05b# date
Mon Aug 22 03:20:50 UTC 2016
bash-2.05b# date -s "2016/08/22 23:21:00"
Mon Aug 22 23:21:00 UTC 2016
bash-2.05b# 

21) Modify the Sked A2: "Skeduler A1" Dial-out Days/Times Presets as necessary.
