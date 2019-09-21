import sys
from subprocess import call

sys.path.append("/media/mmcblk0p1/amigos/ext")
try:
    # create missing folder and fil
    call("bash /media/mmcblk0p1/amigos/bash/missing", shell=True)
except Exception as err:
    print(err)
