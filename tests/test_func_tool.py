from typing import Dict, Any, AnyStr
from sgtpyutils.functools import AssignableArg


class TargetType:
    def __init__(self, value) -> None:
        self.value = value


def require_by_type(method):
    def wrapper(*args, **kwargs):
        arg = AssignableArg(args, kwargs, method)
        arg.assign_by_type(TargetType, TargetType(1))
        arg.assign_by_type(int, 2)
        return method(*arg.args, **arg.kwargs)
    return wrapper


@require_by_type
def target_func1(testInt: int, testType: TargetType):
    return testInt, testType


def test_auto_assign_by_type():
    result = target_func1()
    assert result[0] == 2
    assert result[1].value == 1


def require_by_name(method):
    def wrapper(*args, **kwargs):
        arg = AssignableArg(args, kwargs, method)
        arg.assign_if_not_assigned('assigned', 11)
        arg.assign_if_not_assigned('not_assigned', 12)
        arg.assign_if_not_exist('kw_arg', 13)
        return method(*arg.args, **arg.kwargs)
    return wrapper


@require_by_name
def target_func2(assigned: int, not_assigned: int, **kwargs):
    return assigned, not_assigned, kwargs


def test_auto_assign_by_name():
    assigned, not_assigned, kwargs = target_func2(1)
    assert assigned == 1
    assert not_assigned == 12
    assert kwargs.get('kw_arg') == 13


class ATypeClass:
    def __init__(self, a) -> None:
        self.a = a


AType = ATypeClass

xDict = Dict[Any, Any]
xStr = str


def require_by_name(method):
    def wrapper(*args, **kwargs):
        arg = AssignableArg(args, kwargs, method)
        current_value = arg.get_assign_by_type(xDict)
        assert current_value['v'] == 3

        current_value = arg.get_assign_by_type(xStr)
        assert current_value == '2'

        return method(*arg.args, **arg.kwargs)
    return wrapper


@require_by_name
def func_to_assign(a: AType, b: xStr, c: xDict, d: Dict):
    return a


def test_get_assign():
    func_to_assign(AType(1), '2', {'v': 3}, {'v': 4})
