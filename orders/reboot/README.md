# Rebooting

This order can be used to reboot the system.

**WARNING**: Read instructions carefully before performing this operation.

## How to use

Since the supervise task will run immediately after reboot (hence so will the reboot order), it is necessary to use a file to indicate whether the reboot was performed already to avoid a rebooting continually.

You need to ensure this file does not already exist prior to submitting this order, or else the reboot will not be performed. Therefore this order generally requires two separate steps.

1. Stage the `remove_rebooted_file.sh` order script

    ```scp remove_rebooted_file.sh nusnow:/disks/restricted_ftp/amigos3a/orders```

1. Wait for confirmation of successful removal
1. Clear the staged order directory

    ```ssh nusnow -c "rm /disks/restricted_ftp/amigos3a/orders/*"```

1. Stage the `reboot.py` order script

    ```scp reboot.py nusnow:/disks/restricted_ftp/amigos3a/orders```

1. Wait for confirmation of successful reboot
1. Clear the staged order directory

    ```ssh nusnow -c "rm /disks/restricted_ftp/amigos3a/orders/*"```
