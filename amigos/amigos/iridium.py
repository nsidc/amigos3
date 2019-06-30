from serial import Serial as ser


def send(message):
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print('Unable to open port')
        return
    port.write(message)

    return read()


def read():
    try:
        port = ser('/dev/ttyS1')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print('Unable to open port')
        return None
    rev = port.read(port.inWating())
    return rev
