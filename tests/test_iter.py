from sgtpyutils.extensions.itertools import *


def test_iter():
    for index, x in run_cycle('123', length=3):
        pass
    assert index == 27 -1

def test_iter_full():
    for index, x in run_cycle_full('123', length=3):
        pass
    assert index == 3 + 9 + 27 - 1  # 从0开始故-1，每级指数3
