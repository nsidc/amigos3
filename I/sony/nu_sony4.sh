#!/bin/sh

# this script takes 6 images from the SonyCam on A22A
# modified by RR 5/11/06

SONYFILE_01=/mnt/upload_images/Sony_01.jpg
SONYFILE_02=/mnt/upload_images/Sony_02.jpg
SONYFILE_03=/mnt/upload_images/Sony_03.jpg

SONYFILE_04=/mnt/upload_images/Sony_04.jpg
SONYFILE_05=/mnt/upload_images/Sony_05.jpg
SONYFILE_06=/mnt/upload_images/Sony_06.jpg
SONYFILE_txt=/mnt/upload_images/dummy.txt

SONYPICTUREURL=http://192.168.0.20:8082/oneshotimage.jpg
# PTZ speed to manual
SONYPTZURL_01=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101062403FF

# A22A Zoom number 1 looking down at orange marker pole 
# was this 8101044700000000ff now is this 8101044701080000ff RR 5/11/06
SONYZOOMURL_01=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044701060104ff 
# A22A Zoom number 2 looking down at horizon                
# was 8101044703080000ff now is 8101044700000000ff which is nx10 RR 5/21/06 
SONYZOOMURL_02=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044703080e01ff 
# now make move 3 to nx13 RR 5/22/06                                                                                    
#SONYZOOMURL_03=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=81010447030a020eff
# now make move 3 4 steps up on pos 2 RR 8/27/06 
SONYZOOMURL_03=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044703080e01ff
# now make move 4 to nx14 RR 5/22/06 
SONYZOOMURL_04=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044703080e01ff
# A22A Zoom number 5 looking down at barrel 8101044702080000ff
SONYZOOMURL_05=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044702080000ff
# A22A Zoom number 6 looking down at solar panels 8101044700000000ff
SONYZOOMURL_06=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101044700000000ff

# A22A angle number 1 looking down at orange marker pole 
# was this 8101060214140002060a0000030cff now is this 81010602141400020b080f0f0f0cff RR 5/11/06 
SONYMOVEURL_01=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=81010602141400020b080f0f0f0cff
# A22A angle number 2 looking down at the flags 5/22/06        
SONYMOVEURL_02=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101060214140000090b0f0e0206ff
# pos 3 was this 
# SONYMOVEURL_03=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101060218140000090b0f0e020bff
# A22A angle number 3 looking down at the flags but 4 steps up from pos 2 8/27/06
SONYMOVEURL_03=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101060218140000090b0f0e0107ff
SONYMOVEURL_04=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=8101060218140f0c0e010f0e0107ff
# A22A angle number 5 looking down at barrels 810106021414000304080f0e0f0aff
SONYMOVEURL_05=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=810106021414000304080f0e0f0aff
# A22A angle number 6 looking down at solar panels 810106021414000000000003030cff
SONYMOVEURL_06=http://192.168.0.20:8082/command/ptzf.cgi?VISCA=810106021414000000000003030cff

echo "set auto-pan-tilt to off"
wget $SONYPTZURL_01 -O $SONYFILE_txt
sleep 3
echo "Trying to move camera pos 4"
wget $SONYZOOMURL_04 -O $SONYFILE_txt
wget $SONYMOVEURL_04 -O $SONYFILE_txt
sleep 3
echo "Trying to read picture " 
wget $SONYPICTUREURL -O $SONYFILE_04
sleep 3
exit 0
