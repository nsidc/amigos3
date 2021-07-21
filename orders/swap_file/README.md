# Swapping a file

This order can be used to swap a single file on the SD card. This is useful for deploying a fix to a python file to fix a bug, for example, and could be modified for multiple files.

**WARNING**: Making changes to the operating code is _VERY DANGEROUS_ and could result in a broken system. Be very careful about making changes and thoroughly test before making the order.

## How to use

1. Change the value of the variable `CURRENT_FILE` in 'install.sh' to the full path of the file you wish to replace on the AMIGOS system (e.g. `/media/mmcblk0p1/honcho/core/system.py`)
1. Place the file you wish to replace it with in this directory and name it the same as `CURRENT_FILE` but with the postfix `.new` (e.g. `./system.py.new`)
1. Put checksums for the relevant files as expected *before* the operation in 'initial.md'

    ```
    md5sum install.ssh > initial.md5
    md5sum /media/mmcblk0p1/honcho/core/system.py >> initial.md5
    md5sum system.py.new >> initial.md5
    md5sum system.py.current >> initial.md5
    ```

1. Put checksums for the relevant files *after* the operation in 'final.md'

    ```
    md5sum /media/mmcblk0p1/honcho/core/system.py >> final.md5
    ```

1. Verify files for order are correct and complete in this working directory (don't forget executable permissions if file to be substituted must be executable!)
1. Move files for order into place on 'restricted_ftp' for appropriate tower to pick them up

    ```scp ./* nusnow:/disks/restricted_ftp/amigos3a/orders```

1. Wait for tower to pick up and perform orders. When performed, the tower should upload the output from the script(s) and send an 'ORD' SBD message with a 0 status if successful.
1. Clear the orders (otherwise tower will repeat them next round)

    ```ssh nusnow -c "rm /disks/restricted_ftp/amigos3a/orders/*"```
