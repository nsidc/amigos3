#!/bin/bash
set -ex

# Get script dir and cd to it
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# MODIFY THIS TO BE THE FILE TO BE REPLACED ON THE AMIGOS
CURRENT_FILE="/media/mmcblk0p1/honcho/core/system.py"
# File to replace it should have same name but with '.new' appended and accompany this script

CURRENT_FILENAME=`basename $CURRENT_FILE`
CURRENT_FILE_BACKUP="${DIR}/${CURRENT_FILENAME}.current"
CURRENT_FILE_BACKUP="${DIR}/${CURRENT_FILENAME}.new"

# Backup current configuration to modify
cp $CURRENT_FILE $CURRENT_FILE_BACKUP

# Verify initial state checksums
if md5sum -c "${DIR}/initial.md5"; then
    echo 'Starting checksums OK'
else
    echo 'Starting checksums FAILED'
    exit 1
fi

# Install new files
cp $REPLACEMENT_FILE $CURRENT_FILE

# Verify final state checksums
if md5sum -c "${DIR}/final.md5"; then
    echo 'Final checksums OK'
else
    echo 'Final checksums FAILED. Reverting...'
    cp $CURRENT_FILE_BACKUP $CURRENT_FILE
    exit 1
fi
