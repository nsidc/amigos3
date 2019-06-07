from serial import Serial as ser


def send(message):
    try:
        port = ser('/dev/ttyS3')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print('Unable to open port')
        return
    port.write(message)


def read(message):
    try:
        port = ser('/dev/ttyS3')
        port.baudrate = 115200
        port.open()
        port.flushInput()
    except:
        print('Unable to open port')
        return None
    rev = port.readline(message)
    return rev
