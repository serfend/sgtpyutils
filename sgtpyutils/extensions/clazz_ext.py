import inspect
import sys


class T:
    TA: str = None


def setups(target: type, names: list):
    [setup(target, x) for x in names]


def setup(target: type, name: str):
    n = '__name__'

    def PredicateProperty(v):
        r = type(v) == type(T.TA)
        if not r:
            return r
        if not hasattr(v, n) or getattr(v, n) in ['__doc__']:
            return False
        return r

    def PredicateFunction(v):
        r = type(v) == type(setup)
        if not r:
            return False
        if getattr(v, n) in ['setup', 'setups']:
            return False
        return True

    def MemberPredict(v):
        r = PredicateProperty(v)
        r |= PredicateFunction(v)
        return r
    if not name in sys.modules:
        __import__(name)
    m = sys.modules[name]
    members = inspect.getmembers(m, MemberPredict)
    [setattr(target, x[0], x[1]) for x in members]
