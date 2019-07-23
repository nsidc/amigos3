import os
import sys
from subprocess import call

# create missing folder and files
try:
    call("bash /media/mmcblk0p1/bash/missing > /dev/null", shell=True)
except:
    pass
# Put the submodules on the python import path
this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(this_dir, '../ext/urllib3/src'))
sys.path.append(os.path.join(this_dir, '../ext/chardet'))
sys.path.append(os.path.join(this_dir, '../ext/idna'))
sys.path.append(os.path.join(this_dir, '../ext/requests'))
sys.path.append(os.path.join(this_dir, '../ext/pynmea2'))
sys.path.append(os.path.join(this_dir, '../ext/PyCampbellCR1000'))
sys.path.append(os.path.join(this_dir, '../ext/PyLink'))
