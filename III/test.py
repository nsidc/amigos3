import binascii as bina
n = ''
with open('gps_binex_data.log', 'rb') as fil:
    m = fil.readline()
    # print(m)
    for b in m:
        h = bina.b2a_uu(b)[0:-2]
        # if '\n' in h:
        #     print('hey')
        if h != '\n':
            n = n+h
with open('text.log', 'w') as logg:
    logg.write(n)
print(n)
