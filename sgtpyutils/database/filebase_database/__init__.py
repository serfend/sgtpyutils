from __future__ import annotations
import pathlib2
from functools import wraps
import os
from sgtpyutils.functools import *
import json


class Database:
    '''
    基于文件的db，仅允许加载json文件
    '''
    cache: dict[str, dict] = {}

    def __init__(self, database: str) -> None:
        self.is_abs = pathlib2.Path(database).is_absolute()
        self.database = database
        if self.is_abs:
            self.base_path = ''
        else:
            root_path = pathlib2.Path(
                __file__).parent.parent.parent.joinpath('database')
            self.base_path = f'{root_path}{os.sep}'
        self.load_db()

    def check_file(self):
        xxx = pathlib2.Path(self.database_filename)
        if not xxx.parent.is_dir():
            os.makedirs(xxx.parent.as_posix())
        if not xxx.exists():
            with open(xxx.as_posix(),'w') as f:
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
        Database.cache[self.database] = self

    def save(self):
        self.check_file()

        with open(self.database_filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.value))

    @property
    def database_filename(self) -> str:
        '''
        only allow .json file
        '''
        return f'{self.base_path}{self.database}.json'

    @property
    def value(self) -> dict:
        return Database.cache[self.database].raw_value

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
