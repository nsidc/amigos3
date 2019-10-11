from collections import namedtuple

_Unit = namedtuple('Unit', ('name', 'mac_address', 'seabird_ids'))


units = namedtuple('UNITS', ('amigos3a', 'amigos3b', 'amigos3c'))(
    _Unit(
        name='amigos3a',
        mac_address='',
        seabird_ids=['90', '??'],
        aquadopp_ids=['20', '21'],
    ),
    _Unit(
        name='amigos3b',
        mac_address='',
        seabird_ids=['05', '09'],
        aquadopp_ids=['22', '23'],
    ),
    _Unit(
        name='amigos3c',
        mac_address='',
        seabird_ids=['06', '80'],
        aquadopp_ids=['26', '27'],
    ),
)
