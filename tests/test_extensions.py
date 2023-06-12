import sgtpyutils.extensions
import sgtpyutils.extensions.clazz
from sgtpyutils.extensions.itertools import run_cycle
from sgtpyutils.hash import HashAlgo, get_hash


def test_fields():
    class TestA:
        def __init__(self) -> None:
            self.A1 = 0
            self.A2 = '0'

    class TestB(TestA):
        def __init__(self) -> None:
            super().__init__()
            self.B1 = '1'
    fields = sgtpyutils.extensions.clazz.get_fields(TestB(), with_parent=False)
    assert 'A1' not in fields
    assert 'B1' in fields
    assert fields['B1'] == '1'
    fields = sgtpyutils.extensions.clazz.get_fields(TestB(), with_parent=True)
    assert 'A1' in fields
    assert 'B1' in fields
    assert fields['A1'] == 0

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


def test_cycle():
    a = run_cycle('123abc456', 10)
    result = [''.join(x[1]) for x in a]
    assert len(result) == 10
    assert result == ['11', '21', '31', 'a1',
                      'b1', 'c1', '41', '51', '61', '12']

    import string
    a = run_cycle(string.digits, 10)
    result = [''.join(x[1]) for x in a]
    assert len(result) == 10
    assert result == ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    a = run_cycle(string.digits, length=1)
    result = [''.join(x[1]) for x in a]
    assert len(result) == 10
    assert result == ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    a = run_cycle(string.digits, length=2)
    result = [''.join(x[1]) for x in a]
    assert len(result) == 100
    t = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    r = []
    for i in range(10):
        r += [f'{x}{i}' for x in t]
    assert result == r


def test_hash():
    get_hash('123456', HashAlgo.md5) == 'e10adc3949ba59abbe56e057f20f883e'
    get_hash('123456', HashAlgo.sha1) == '7c4a8d09ca3762af61e59520943dc26494f8941b'

def test_dict2obj():
    class X:
        def __init__(self) -> None:
            self.a = 0
    x = {'a':1}

    dict2obj = sgtpyutils.extensions.clazz.dict2obj
    x:X = dict2obj(X(),x)
    assert x.a == 1
def test_list2dict():
    a = [2,4,7]
    list2dict = sgtpyutils.extensions.list2dict
    x = list2dict(a)
    assert x.get(0) == 2
    assert x.get(1) == 4
    assert x.get(2) == 7