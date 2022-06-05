import sgtpyutils.extensions
def test_flat():
    flat = sgtpyutils.extensions.flat
    items = ['1', '2', '3', '4', '5']
    assert items == flat(['1', ['2', '3'], '4', ['5']])
    assert items == flat([[['1']], ['2', ['3', '4'], '5']], 2)


def test_find():
    find = sgtpyutils.extensions.find
    items = ['1', '2', '3', '4', '5']
    assert '3' == find(items, lambda x: x == '3')
    assert '3' == find(items, lambda x: int(x) == 3)
    assert '3' == find(items, lambda x, index: index == 2)
    assert None == find(items, lambda x, index: index == 7)