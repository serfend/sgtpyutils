import pathlib2
from functools import wraps
import os
from hikapi.common_utils.functools import assign_by_type
from hikapi.api.libs import *
import json
import atexit


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DateTime):
            return obj.tostring()
        else:
            return json.JSONEncoder.default(self, obj)


class Database:
    cache: dict[str, dict] = {}
    root_path: str = None

    def __init__(self, database: str) -> None:
        atexit.register(self.save)
        self.database = database

        self.base_path = f'{Database.root_path}{os.sep}'
        self.load_db()

    def check_file(self):
        xxx = pathlib2.Path(self.database_filename)
        if not xxx.parent.is_dir():
            os.makedirs(xxx.parent.as_posix())
        if not xxx.exists():
            with open(xxx.as_posix(), 'w') as f:
                pass

    def load_db(self, reload: bool = False):
        if not reload and Database.cache.get(self.database):
            return Database.cache.get(self.database)
        self.check_file()
        with open(self.database_filename, 'r', encoding='utf-8') as f:
            data = f.read()
            if len(data) < 3:
                data = '{}'
            self.raw_value = json.loads(data)
        Database.cache[self.database] = self.raw_value

    def save(self):
        self.check_file()

        with open(self.database_filename, 'w', encoding='utf-8') as f:
            data = self.value
            data_raw = json.dumps(data, cls=DateEncoder)
            f.write(data_raw)

    @property
    def database_filename(self) -> str:
        return f'{self.base_path}{self.database}.json'

    @property
    def value(self) -> dict:
        return Database.cache[self.database]

    def get(self, key: str, default: any = None) -> dict:
        if not key in self.value:
            self.value[key] = default
        return self.value.get(key)

    @staticmethod
    def require_database(db_path: str):
        def func(target_mathod: function):
            @wraps(target_mathod)
            def wrapper(*args, **kwargs):
                db = Database(db_path)
                assign_by_type(args, kwargs, target_mathod, Database, db)
                return target_mathod(*args, **kwargs)
            return wrapper
        return func


__x = pathlib2.Path(__file__)
__x = __x.parent.parent.parent.joinpath('database')
Database.root_path = __x
