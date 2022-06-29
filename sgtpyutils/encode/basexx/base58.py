if str != bytes:
    # Python 3.x
    def ord(c):
        return c

    def chr(n):
        return bytes((n,))

table = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
table_size = len(table)
decode_table = dict((v, k) for k, v in enumerate(table))


def b58encode(v):
    int_val = 0
    for (i, c) in enumerate(v[::-1]):
        int_val += (256**i) * ord(c)

    result = []
    while int_val >= table_size:
        div, mod = divmod(int_val, table_size)
        result.append(table[mod])
        int_val = div
    result.append(table[int_val])

    padding = 0
    for c in v:
        if c == '\x00':
            padding += 1
        else:
            break

    result += [table[0]*padding]
    return ''.join(result)[::-1]


def b58decode(v):
    int_val = 0
    for (i, c) in enumerate(v[::-1]):
        int_val += decode_table[c] * (table_size**i)

    result = bytearray()
    while int_val >= 256:
        div, mod = divmod(int_val, 256)
        result.append(mod)
        int_val = div
    result.append(int_val)

    padding = 0
    for c in v:
        if c == table[0]:
            padding += 1
        else:
            break

    result += b'\x00' * padding
    return bytes(result)[::-1]
