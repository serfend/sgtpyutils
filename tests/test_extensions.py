import sgtpyutils.extensions


def test_flat():
    flat = sgtpyutils.extensions.flat
    items = ['1', '2', '3', '4', '5']
    assert items == flat(['1', ['2', '3'], '4', ['5']])
    assert items == flat([[['1']], ['2', ['3', '4'], '5']], 2)
    assert items == flat([[['1']], ['2', ['3', ['4']], '5']])


def test_find():
    find = sgtpyutils.extensions.find
    items = ['1', '2', '3', '4', '5']
    assert '3' == find(items, lambda x: x == '3')
    assert '3' == find(items, lambda x: int(x) == 3)
    assert '3' == find(items, lambda x, index: index == 2)
    assert None == find(items, lambda x, index: index == 7)


def test_convert_bytes():
    convert = sgtpyutils.extensions.cast2bytes
    assert convert(b'123') == b'123'
    assert convert('123') == b'123'
    assert convert((1 << 8)+(2 << 4)+(3 << 0)) == b'\x01\x23'
    assert convert(['1', '2', '3']) == b'123'
    assert convert(['12', '3']) == b'123'
    assert convert(['1', [[['2']], '3']]) == b'123'
    assert convert(['测', [[['试']], '3']]) == '测试3'.encode('utf-8')


def test_xor():
    xor = sgtpyutils.extensions.xor
    assert xor(1, 0) == b'\x01'
    assert xor(
        123, 321) == b'\x7a', '123 ^ 321 = \x7b ^ 0x0141 = \x7b ^ \0x01 == \x7a'
    assert xor('123', '123') == b'\x00\x00\x00'
    key = bytearray.fromhex('057D411526')
    v = b'~!3a@'
    assert xor(b'{\\rtf', key) == v
    assert xor([b'{\\', b'rtf', ], key) == v
