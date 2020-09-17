#!/bin/bash
set -ex

# Get script dir and cd to it
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# Copy current configuration to modify
cp /media/mmcblk0p1/honcho/config.py $DIR

# Verify initial state checksums
if md5sum -c "${DIR}/initial.md5"; then
    echo 'Starting checksums OK'
else
    echo 'Starting checksums FAILED'
    exit 1
fi

# Modify configuration
cat <<EOT >> "${DIR}/config.py"

try:
    from config_override import *
except:
    pass
EOT

# Verify final state checksums
if md5sum -c "${DIR}/final.md5"; then
    echo 'Final checksums OK'
else
    echo 'Final checksums FAILED'
    exit 1
fi

# Install new configuration
cp "${DIR}/config.py" /media/mmcblk0p1/honcho/
cp "${DIR}/config_override.py" /media/mmcblk0p1/honcho/
