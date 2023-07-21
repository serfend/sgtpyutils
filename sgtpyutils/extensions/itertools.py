from itertools import *
from typing import List


def get_end_by_length(table: any, length: int):
    return len(table) ** length


def run_cycle_full(table: List, end: int = -1, length: int = -1, start: int = 0):
    '''
    see run_cycle.
    equal to `for i in range(length):run_cycle(i...)`
    '''
    if length <= 0:
        return run_cycle(table, end, length, start)
    cur_index = 0
    for i in range(length):
        x_length = i+1
        for index, x in run_cycle(table, end, x_length, start):
            yield (cur_index + index, x)
        cur_index += (index+1) # accumulate last cycle

def run_cycle(table: List, end: int = -1, length: int = -1, start: int = 0):
    '''
    get a iter of tables-cycle
    Arguments:
    table:str|List the table of string-collectin
    end:int end of iter, if not set , one-cycle of table will return
    length:int length of cycle-string
      if length is set , `end` will be ignored
    start:int from what to return
    Example:
      > import string
      > a = run_cycle(string.digits,10)
      > for index,i in a:
      >   print(index,''.join(i))

      > 0 0
        1 1
        2 2
        3 3
        4 4
        5 5
        6 6
        7 7
        8 8
        9 9

      > a = run_cycle('123abc456',10)
      > for index,i in a:
      >   print(i)

      > (0, ['1', '1'])
        (1, ['2', '1'])
        (2, ['3', '1'])
        (3, ['a', '1'])
        (4, ['b', '1'])
        (5, ['c', '1'])
        (6, ['4', '1'])
        (7, ['5', '1'])
        (8, ['6', '1'])
        (9, ['1', '2'])

      > import string
      > a = run_cycle(string.digits,length=1)
      > for index,i in a:
      >   print(index,''.join(i))

      > 0 0
        1 1
        2 2
        3 3
        4 4
        5 5
        6 6
        7 7
        8 8
        9 9
    '''
    if length > 0:
        end = get_end_by_length(table, length)
    if isinstance(table, str):
        table = [x for x in table]
    table_size = len(table)

    def int2table(v: int) -> List:
        r = []
        while v >= table_size:
            r.append(v % table_size)
            v //= table_size
        r.append(v)
        return r

    table_start = int2table(start)
    table_end = int2table(end-1)
    table_start += [0]*(len(table_end)-len(table_start))

    base_str = [table[x] for x in table_start]

    def accumulate(index: int = 0):
        table_start[index] += 1
        if table_start[index] >= table_size:
            table_start[index] = 0
            base_str[index] = table[0]
            return accumulate(index+1)
        base_str[index] = table[table_start[index]]

    yield 0, base_str
    for i in range(start+1, end):
        accumulate()
        yield i, base_str
