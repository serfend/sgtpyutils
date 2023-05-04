import inspect
from typing import Callable, Dict, List


def convert_to_value(i: object, clazz: type, callback: Callable):
    '''
    将i转换为目标值
    '''
    if isinstance(i, int):
        return i
    elif clazz == i.__class__:
        return callback(i)
    else:
        raise Exception('invalid input')


def get_data(item: object, fields_mapper: List) -> Dict:
    '''
    get data from a object with fields specified
    '''
    result = {}
    tstring = type('')
    tarray = type([])
    for i in fields_mapper:
        ti = type(i)
        if ti == tstring:
            result[i] = getattr(item, i)
        elif ti == tarray:
            result[i[0]] = i[1](item)
        else:
            raise Exception('invalid operation')
    return result


def get_fields(data: any, with_parent: bool = True):
    '''
    get instance fields
    @param with_parent bool = True: whether to get parent fileds
    '''
    r = dict([[k, getattr(data, k)] for k in dir(data)])
    result = {}
    if not with_parent:
        p = dict([[k,None] for k in dir(data.__class__.__base__())])
        for x in r:
            if not x in p:
                result[x] = r[x]
    else:
        result = r
    return result


def class2props(obj: object):
    '''
    将class转dict,以_开头的属性不要
    '''
    if isinstance(obj, dict):
        return obj
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)

        if not name.startswith('__') and not inspect.isbuiltin(value) and not inspect.isfunction(value) and not name.startswith('_'):
            pr[name] = value
    return pr


def class2props_with_(obj: object) -> Dict:
    '''
    将class转dict,以_开头的也要
    '''
    if isinstance(obj, dict):
        return obj
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.isbuiltin(value) and not inspect.isfunction(value):
            pr[name] = value
    return pr


def dict2obj(obj: object, dict: Dict) -> object:
    '''
    dict转obj，先初始化一个obj
    '''
    obj.__dict__.update(dict)
    return obj
