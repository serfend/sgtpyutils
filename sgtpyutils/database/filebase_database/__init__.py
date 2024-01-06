import pathlib2
from functools import wraps
import os
import json
import atexit
from sgtpyutils.datetime import DateTime
from sgtpyutils.functools import AssignableArg


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DateTime):
            return obj.tostring()
        return json.JSONEncoder.default(self, obj)


class Database:
    cache: dict[str, dict] = {}
    root_path: str = None
    raw_value: dict
    '''数据原始对象'''
    database: str
    '''数据库名称'''

    def __init__(self, database: str) -> None:
        atexit.register(self.save)
        self.database = database

        self.load_db()

    def check_file(self):
        return Database.ensure_file(self.database_filename)

    @staticmethod
    def ensure_file(path: str):
        xxx = pathlib2.Path(path)
        if not xxx.parent.is_dir():
            os.makedirs(xxx.parent.as_posix())
        if not xxx.exists():
            with open(xxx.as_posix(), 'w'):
                pass

    def load_db(self, reload: bool = False):
        if not reload:
            if Database.cache.get(self.database) is not None:
                self.raw_value = Database.cache.get(self.database)
                return self.raw_value

        self.check_file()
        with open(self.database_filename, 'r', encoding='utf-8') as f:
            data = f.read()
            if len(data) < 3:
                data = '{}'
            self.raw_value = json.loads(data)
        Database.cache[self.database] = self.raw_value
        return self.raw_value

    def save(self):
        if hasattr(self, 'is_deleted'):
            return False
        if Database.cache.get(self.database) is None:
            return  # 已被删除
        return Database.save_direct(self.database_filename, self.raw_value)

    @staticmethod
    def save_direct(path: str, data: dict):
        Database.ensure_file(path)

        with open(path, 'w', encoding='utf-8') as f:
            data_raw = json.dumps(data, cls=DateEncoder, ensure_ascii=False)
            f.write(data_raw)

    @property
    def database_filename(self) -> str:
        '''文件完整路径'''
        return Database._database_filename(self.database, self.base_path)

    def _database_filename(data: str, base: str = None) -> str:
        if base is None:
            base = Database.get_base_path(data)
        return f'{base}{data}.json'

    @property
    def base_path(self):
        if hasattr(self, '_basepath'):
            return self._basepath
        self._basepath = Database.get_base_path(self.database)
        return self._basepath

    @staticmethod
    def get_base_path(database: str):
        base_path: str
        '''基础路径，当使用相对路径时使用'''
        is_abs: bool
        '''是否是绝对路径，影响base_path'''

        is_abs = pathlib2.Path(database).is_absolute()
        if is_abs:
            base_path = ''
        else:
            current = pathlib2.Path(__file__).parent.parent.parent
            root_path = current.joinpath('database')
            base_path = f'{root_path}{os.sep}'
        return base_path

    @property
    def value(self) -> dict:
        return Database.cache[self.database]

    def get(self, key: str, default: any = None) -> dict:
        if key not in self.value:
            self.value[key] = default
        return self.value.get(key)

    @staticmethod
    def require_database(db_path: str):
        def func(target_mathod: callable):
            @wraps(target_mathod)
            def wrapper(*args, **kwargs):
                db = Database(db_path)
                arg = AssignableArg(args, kwargs, target_mathod)
                arg.assign_by_type(Database, db)
                return target_mathod(*arg.args, **arg.kwargs)
            return wrapper
        return func

    @staticmethod
    def save_all():
        for x in Database.cache:
            data = Database.cache[x]
            path = Database._database_filename(x)
            Database.save_direct(path, data)

    def delete(self):
        self.is_deleted = True
        if Database.cache.get(self.database) is not None:
            del Database.cache[self.database]

        path = self.database_filename
        if not os.path.exists(path):
            return
        os.remove(path)


__x = pathlib2.Path(__file__)
__x = __x.parent.parent.parent.joinpath('database')
Database.root_path = __x
