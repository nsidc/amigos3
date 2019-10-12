import os
import pty
import threading

from serial import Serial

import pytest


@pytest.fixture
def serial_mock(listener, baud):
    '''
    Mocked serial port with responses dictated by listener
    '''
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)

    # create a separate thread that listens on the master device for commands
    thread = threading.Thread(target=listener, args=[master])
    thread.start()

    # open a pySerial connection to the slave
    serial = Serial(s_name, baud, timeout=1)

    yield serial

    serial.close()
