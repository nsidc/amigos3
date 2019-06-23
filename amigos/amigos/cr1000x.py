import datetime
from pycampbellcr1000 import CR1000


def test():
    device = CR1000.from_url('tcp:192.168.0.30:6785')
    data = device.get_data('Public')
    print(data[0])
