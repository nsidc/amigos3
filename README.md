# The AMIGOS III operations system and command line interface

[![Build Status](https://travis-ci.com/wallinb/amigos3.svg?branch=master)](https://travis-ci.com/wallinb/amigos3)
[![codecov](https://codecov.io/gh/wallinb/amigos3/branch/master/graph/badge.svg)](https://codecov.io/gh/wallinb/amigos3)

## Dependencies

### AMIGOS dependencies

The AMIGOS stations have no package management, therefore submodules are used to install dependencies for the AMIGOS operating software. These are checked out under the `./ext` subdirectory and copied to the station on deployment.

1. Initialize submodules (run in repository root directory)

    ```
    $ git submodule init && git submodule update
    ```

### Operator dependencies

Operations are performed from a unix-like system with typical tasks defined in the `Makefile`.

The following utilities are assumed to be available locally:

* make
* picocom
* ssh/scp
* rsync


### Development dependencies

Dependencies in the development environment are managed with [Conda](https://docs.conda.io/en/latest/index.html).

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anoconda](https://www.anaconda.com/distribution/)

1. Create the environment (run in repository root directory)

    ```
    $ conda env create -f environment.yml
    ```

    This will create a 'amigos' environment with the correct version of python and dependencies for the project.

1. Activate the environment

    ```
    $ conda activate amigos-test-env
    ```

1. Install amigos CLI commands (local to source directory)

    ```
    $ python setup.py develop
    ```

## Running tests

Due to poor support for Python 2.6, tests are run in a separate Python 2.7 environment

    ```
    $ make test
    ```

## Operating the station

The `Makefile` includes commands for common tasks for operation the stations.


### Connect to the JTAG serial terminal interface

This interface enables terminal interaction as well as outputs system logging.

1. Open the white enclosure and connect serial-to-usb cable to JTAG serial port and laptop USB port
1. Run

    ```
    $ make serial-con
    ```

1. Login when prompted


### Connect via SSH

1. Connect your laptop to the AMIGOS white box "Comp" ethernet port
1. Make sure your laptop ethernet connection is configured with the static IP 192.168.0.33
1. From the "amigos3" repository directory, run

    ```
    $ make ssh-con
    ```

1. Login when prompted


### Deploy "Honcho" operating code to the AMIGOS station SD card

To deploy the "Honcho" AMIGOS operating code from your laptop to the AMIGOS station

1. If you haven't already, initialize submodules (requires internet connection)

    ```
    $ make submodules
    ```

1. Connect your laptop to the AMIGOS white box "Comp" ethernet port
1. Make sure your laptop ethernet connection is configured with the static IP 192.168.0.33
1. From the "amigos3" repository directory, run

    ```
    $ make sync-code
    ```


### Deploy "Honcho" system configuration files to the AMIGOS station onboard Flash memory

1. Connect your laptop to the AMIGOS white box "Comp" ethernet port
1. Make sure your laptop ethernet connection is configured with the static IP 192.168.0.33
1. From the "amigos3" repository directory, run

    ```
    $ make sync-system
    ```


### Make a timestamped backup of the AMIGOS SD card

1. Connect your laptop to the AMIGOS white box "Comp" ethernet port
1. Make sure your laptop ethernet connection is configured with the static IP 192.168.0.33
1. From the "amigos3" repository directory, run

    ```
    $ make backup
    ```

The entire SD card (including "honcho" code and data) will be copied to `./backup/`.


## The "honcho" operating code interface

The "honcho" operating software has a CLI interface to facilitate performing operations on the station manually for e.g. testing. For general usage help


    ```
    $ honcho --help
    ```

For usage help of a specific subcommand

    ```
    $ honcho <sub-command> --help
    ```


### Example/useful commands

* `honcho system --shutdown` -- shutdown system
* `honcho system --reboot` -- reboot system
* `honcho system --standby 10` -- standby for 10 minutes
* `honcho gpio --list` -- show current state of GPIO switched elements
* `honcho gpio --hub-on` -- turn on ethernet hub (necessary for SSH)
* `honcho gpio --all-off` -- turn off all peripherals
* `honcho schedule --summary` -- see summary of current schedule
* `honcho onboard --all` -- get status of Triton onboard sensors
* `honcho solar --run` -- perform solar measurement
* `honcho imm --repl` -- access IMM with interactive prompt
* `honcho camera --look WEST` -- point camera to "WEST"
* `honcho camera --snapshot` -- take snapshot to "snapshot.jpg"


### Environment Variables

Several environment variables modify the operating code globally:

| `LOG_LEVEL`          | CRITICAL, ERROR, WARNING, INFO, DEBUG | level of logging                                                                          |
| `MODE`               | NORMAL, SAFE, TEST, WINTER, SUMMER    | mode of operation (e.g. schedule)                                                         |
| `KEEP_AWAKE`         | 0, 1                                  | station will not enter power-saving sleep mode when idle                                  |
| `HUB_ALWAYS_ON`      | 0, 1                                  | do not be powered off after e.g. measurement (useful when debugging/using ssh connection) |
| `SKIP_MAINTENANCE`   | 0, 1                                  | do not perform maintenance actions (data archival, reset schedule etc...)                 |
| `IGNORE_LOW_VOLTAGE` | 0, 1                                  | the station will not go into "hibernation" standby when voltage is below threshold        |

These are set on bootup automatically from the `./bin/set_env.sh` script.
