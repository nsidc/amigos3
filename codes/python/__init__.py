import sys
from subprocess import call

sys.path.append("/media/mmcblk0p1/codes/ext")
try:
    # create missing folder and fil
    call("bash /media/mmcblk0p1/codes/bash/missing", shell=True)
except Exception as err:
    print (err)
