from __future__ import annotations


class AssignableArg:
    def __init__(self, args: tuple, kwargs: dict) -> None:
        self.args = args
        self.kwargs = kwargs

    def set_args(self, index: int, value: any):
        preset = self.args[0:index]
        suffix = self.args[index+1:]
        self.args = preset + tuple([value]) + suffix

    def check_if_exist(self, key: str, method: function) -> tuple[any, int]:
        '''
        检查函数入参是否包含变量
        包含则返回该变量当前的值及序号，否则返回None和-1
        '''
        r = self.kwargs.get(key)
        if r:
            return (r, -1)
        annotations = enumerate(method.__annotations__)
        args_sets = dict([[x, index] for index, x in annotations])
        arg_index = args_sets.get(key)
        if not arg_index is None:
            if len(self.args) > arg_index:
                return (self.args[arg_index], arg_index)  # 当前变量已被包含
        return [None, -1]

    def assign_if_not_exist(self, key: str, value: any, method: function):
        '''
        检查函数入参是否包含变量，如不包含则赋值到kwargs
        '''
        r = self.check_if_exist(key, method)
        if r[0]:
            return
        if r[0] is None and r[1] > -1:
            # 如果存在值但为None，则仅修改args
            self.set_args(r[1], value)
            return
        self.kwargs[key] = value

    def assign_by_type(self, method: function, target_type: type, value: any):
        uargs = method.__annotations__
        for x in uargs:
            if not issubclass(uargs[x], target_type):
                continue  # not taraget type
            self.assign_if_not_exist(x, value, method)
        return self

    def get_assign_by_type(self, method: function, target_type: type):
        uargs = method.__annotations__
        for index, x in enumerate(uargs):
            if not issubclass(uargs[x], target_type):
                continue  # not taraget type
            user = self.args[index] if len(
                self.args) > index else self.kwargs.get(x)
            user = user or self.kwargs.get(x)  # prevent user from empty
            if user:
                return user
        return None


def check_if_exist(key: str, method: function, args: AssignableArg) -> tuple[any, int]:
    return args.check_if_exist(key, method)


def assign_if_not_exist(key: str, value: any, method: function, args: AssignableArg):
    return args.assign_if_not_exist(key, value, method)


def assign_by_type(args: tuple, kwargs: dict, method: function, target_type: type, value: any):
    x_args = AssignableArg(args, kwargs)
    return x_args.assign_by_type(method, target_type, value)


def get_assign_by_type(args: tuple, kwargs: dict, method: function, target_type: type):
    x_args = AssignableArg(args, kwargs)
    return x_args.get_assign_by_type(method, target_type)
