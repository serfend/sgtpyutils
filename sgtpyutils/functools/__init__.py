from __future__ import annotations
import inspect


class AssignableArg:
    def __init__(self, args: tuple = None, kwargs: dict = None, method: function = None) -> None:
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.method = method

    @staticmethod
    def get_method_dict(method: function):
        annotations = enumerate(method.__annotations__)
        args_sets = dict([[x, index] for index, x in annotations])
        return args_sets

    @property
    def method_dict(self):
        return AssignableArg.get_method_dict(self.method)

    def set_args(self, index: int, value: any, method: function = None):
        method = self.method if method is None else method

        preset = self.args[0:index]
        need_append = index - len(preset)  # 当前面的参数没有值时，使用None填充
        if need_append > 0:
            preset = list(preset) + [None] * need_append
            preset = tuple(preset)
        suffix = self.args[index+1:]
        preset = self.check_preset(preset)  # 检查当前kwargs
        self.args = preset + tuple([value]) + suffix

    def check_preset(self, preset: list, method: function = None):
        '''
        检查前缀是否已经有值，有则需要将kwargs中删除
        '''
        method = self.method if method is None else method
        preset_len = len(preset)
        preset_list = list(preset)
        method_dict = self.get_method_dict(method)
        is_updated = False

        keys = [x for x in method_dict]
        for x in keys:
            index = method_dict[x]
            if index < preset_len and preset_list[index] is None:
                # 对前缀且未赋值的实施
                if x in self.kwargs:
                    # 如果kw中有则覆盖，否则使用默认值
                    preset_list[index] = self.kwargs[x]
                    del self.kwargs[x]
                else:
                    preset_list[index] = self.assign_default_value(x, method)
                    pass
                is_updated = True
        if not is_updated:
            return preset
        self.args = tuple(preset_list)
        return self.args

    def assign_default_value(self, key: str, method: function = None):
        '''get argument default-value'''
        method = self.method if method is None else method
        params = inspect.signature(method).parameters
        p_dict = dict([[x, params[x]] for x in params])
        return p_dict[key].default

    def check_if_exist(self, key: str, method: function = None) -> tuple[any, int]:
        '''
        检查函数入参是否包含变量
        包含则返回该变量当前的值及序号，否则返回None和-1
        '''
        method = self.method if method is None else method

        r = self.kwargs.get(key)
        if r:
            return (r, -1)
        arg_index = self.get_method_dict(method).get(key)
        if not arg_index is None:

            # 判断当前变量已被包含，否则使用其默认值
            if len(self.args) > arg_index:
                v = self.args[arg_index]
            else:
                v = self.assign_default_value(key, method)
            return (v, arg_index)

        return (None, -1)

    def assign_if_not_assigned(self, key: str, value: any, method: function = None) -> bool:
        '''
        检查函数入参是否包含变量且非默认值，如不包含则赋值到kwargs
        @return bool:是否赋值
        '''
        # 已有默认值 或 已传入值 则不赋值
        return self._assign_if_empty(key, value, method, True)

    @staticmethod
    def is_empty(value):
        if value is None:
            return True
        if not issubclass(type(value), type):
            return False
        return issubclass(value, inspect._empty)

    def assign_if_not_exist(self, key: str, value: any, method: function = None) -> bool:
        '''
        检查函数入参是否包含变量，如不包含则赋值到kwargs
        @return bool:是否赋值
        '''
        return self._assign_if_empty(key, value, method, False)

    def _assign_if_empty(self, key: str, value: any, method: function = None, check_arg_index: bool = False):
        method = self.method if method is None else method
        
        _value, _arg_index = self.check_if_exist(key, method)
        if check_arg_index and _arg_index == -1:
            return True
        if not AssignableArg.is_empty(_value):  # empty类型可继续赋值
            return True  # 已有值 不再赋值
        if _arg_index > -1:
            return self.set_args(_arg_index, value, method)
        self.kwargs[key] = value
        return True

    def assign_by_type(self,  target_type: type, value: any, method: function = None):
        method = self.method if method is None else method

        uargs = method.__annotations__
        for x in uargs:
            if not issubclass(uargs[x], target_type):
                continue  # not taraget type
            self.assign_if_not_exist(x, value)
        return self

    def get_assign_by_type(self, target_type: type, method: function = None):
        method = self.method if method is None else method

        uargs = method.__annotations__
        for index, x in enumerate(uargs):
            if not issubclass(uargs[x], target_type):
                continue  # not taraget type
            over = len(self.args) > index
            user = self.args[index] if over else self.kwargs.get(x)
            user = user or self.kwargs.get(x)  # prevent user from empty
            if user:
                return user
        return None


def check_if_exist(key: str, args: AssignableArg) -> tuple[any, int]:
    return args.check_if_exist(key)


def assign_if_not_exist(key: str, value: any, args: AssignableArg):
    return args.assign_if_not_exist(key, value)


def assign_by_type(args: tuple, kwargs: dict, method: function, target_type: type, value: any):
    x_args = AssignableArg(args, kwargs, method)
    return x_args.assign_by_type(target_type, value)


def get_assign_by_type(args: tuple, kwargs: dict, method: function, target_type: type):
    x_args = AssignableArg(args, kwargs, method)
    return x_args.get_assign_by_type(target_type)
