#!/bin/sh

RET=0
./test_return $RET
TEST_RETURN=$?
echo "TEST_RETURN: $TEST_RETURN"
if [ $TEST_RETURN -eq $RET ] ; then
    echo "Got $RET"
else
    echo "Did not get $RET"
fi
