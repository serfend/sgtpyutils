import struct

table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"'
table_size = len(table)
decode_table = dict((v, k) for k, v in enumerate(table))


def b91decode(data: str):
    if isinstance(data, bytes):
        print('excepted content to be a str , assume ascii encode.')
        data = data.decode('ascii')
    v = -1
    b = 0
    n = 0
    result = bytearray()
    for c in data:
        if not c in decode_table:
            continue
        c = decode_table[c]
        if(v < 0):
            v = c
        else:
            v += c * table_size
            b |= v << n
            n += 0xd if (v & 0x1fff) > 0x58 else 0xe
            while True:
                result.append(b & 0xff)
                b >>= 8
                n -= 8
                if not n > 7:
                    break
            v = -1
    if v + 1:
        result.append((b | v << n) & 0xff)
    return bytes(result)


def b91encode(data: bytes):
    if isinstance(data, str):
        print('excepted content to be a bytes , assume utf-8 encode.')
        data = data.encode('utf-8')
    data = bytearray(data)
    b = 0
    n = 0
    result = []
    for count in range(len(data)):
        b |= data[count] << n
        n += 8
        if n > 13:
            v = b & 0x1fff
            if v > 0x58:
                b >>= 13
                n -= 13
            else:
                v = b & 0x3fff
                b >>= 14
                n -= 14
            result.append(table[v % table_size] + table[v // table_size])
    if n:
        result.append(table[b % table_size])
        if n > 7 or b >= table_size:
            result.append(table[b // table_size])
    return ''.join(result)
