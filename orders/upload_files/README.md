# Uploading file(s)

This order puts the specified files on the queue to be uploaded the following day.

WARNING: large files (>10kb) should use the order 'upload_files_large.py' instead.

1. Change the value of the variable `FILEATHS` in 'upload_files.py' to the filepaths of files desired uploaded
1. Move files for order into place on 'restricted_ftp' for appropriate tower to pick them up, e.g.

    ```scp ./* nusnow:/disks/restricted_ftp/amigos3a/orders```

1. Wait for tower to pick up and perform orders. When performed, the tower should upload the output from the script(s) and send an 'ORD' SBD message with a 0 status if successful.
1. Clear the orders (otherwise tower will repeat them next round)

    ```ssh nusnow -c "rm /disks/restricted_ftp/amigos3a/orders/*"```
1. Wait for files to be uploaded to restricted_ftp
1. It is possible the upload does not complete in one day in which case it will be abandoned by the station. In that case you could repeat these steps until success
