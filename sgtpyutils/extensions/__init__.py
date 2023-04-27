
import itertools
from typing import Callable, List
from .typing import cast2bytes



def xor(data: any, xor: any) -> bytes:
    data = cast2bytes(data)
    xor = cast2bytes(xor)
    result = [a ^ b for (a, b) in zip(data, itertools.cycle(xor))]
    return cast2bytes(result)


def find(arr: List, predict: Callable) -> any:
    c_count = predict.__code__.co_argcount
    if c_count == 1:
        def x_predict(i, index): return predict(i)
    elif c_count == 2:
        x_predict = predict
    else:
        raise Exception(f'invalid param count {c_count}')
    for index, i in enumerate(arr):
        if x_predict(i, index):
            return i
    return None


def flat(arr: List, rank: int = -1) -> List:
    if rank == 0:
        return arr
    result = []
    for i in arr:
        if isinstance(i, List):
            result += flat(i, rank-1)
        else:
            result.append(i)
    return result


def distinct(arr: List, predict: Callable = None) -> List:
    '''
    distinct a array
    arr     :   List[T]
    predict :   Callable[T,str]
    '''
    if not predict:
        def predict(x): return x
    dic = {}
    result = []
    for i in arr:
        k = predict(i)
        if k in dic:
            continue
        dic[k] = True
        result.append(i)
    return result
