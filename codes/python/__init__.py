import os
import sys
from subprocess import call
from execp import printf
# create missing folder and files


os.system(
    "source /media/mmcblk0p1/codes/bash/exports.sh")
try:
    call("bash /media/mmcblk0p1/codes/bash/missing", shell=True)
except:
    pass
# Put the submodules on the python import path
# this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append("/media/mmcblk0p1/codes/ext")
# sys.path.append(os.path.join(this_dir, '../ext/chardet'))
# sys.path.append(os.path.join(this_dir, '../ext/idna'))
# sys.path.append(os.path.join(this_dir, '../ext/requests'))
# sys.path.append(os.path.join(this_dir, '../ext/schedule'))
# sys.path.append(os.path.join(this_dir, '../ext/PyCampbellCR1000'))
# sys.path.append(os.path.join(this_dir, '../ext/PyLink'))
