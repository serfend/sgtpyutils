
from __future__ import annotations
from functools import wraps
import traceback
from sgtpyutils.datetime import DateTime
import enum
import pathlib2


class ExceptionHandlerOpt(enum.Flag):
    NoAction = 0
    ResumeRun = 1
    LogFile = 2


class ExceptionHandler:

    @staticmethod
    def path_current(x: DateTime):
        return f'./Exceptions/ex_{x.tostring("%Y%m%d")}.log'

    @staticmethod
    def logExInfo(path: str, exception: Exception):
        data = traceback.format_exception(exception)
        f = pathlib2.Path(path)
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f.absolute().as_posix(), 'a', encoding='utf-8') as out:
            out.write(f'[{DateTime()}]Exception:{data}\n')

    @classmethod
    def handleException(cls, opt: ExceptionHandlerOpt = ExceptionHandlerOpt.ResumeRun | ExceptionHandlerOpt.LogFile, path: callable = path_current):
        def require_func(method: function):
            @wraps(method)
            def wrapper(*args, **kwargs):
                result = None
                try:
                    result = method(*args, **kwargs)
                except Exception as ex:
                    if opt & ExceptionHandlerOpt.LogFile != ExceptionHandlerOpt.NoAction:
                        cls.logExInfo(path(DateTime()), ex)
                    if opt & ExceptionHandlerOpt.ResumeRun != ExceptionHandlerOpt.NoAction:
                        return result
                    raise ex
                return result
            return wrapper
        return require_func
