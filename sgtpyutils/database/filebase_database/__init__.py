import traceback
import threading
import pathlib2
from functools import wraps
import os
import json
from sgtpyutils.datetime import DateTime
from sgtpyutils.functools import AssignableArg
from sgtpyutils.logger import logger
from ..BaseSaver import ISaver


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DateTime):
            return obj.tostring()
        return json.JSONEncoder.default(self, obj)


class DatabaseData:
    def __init__(self, data: dict, serializer: callable, deserializer: callable, name: str = None):
        self.data = data
        self.serializer = serializer
        self.deserializer = deserializer
        self.name = name

    def to_dict(self):
        if self.serializer:
            try:
                result = self.serializer(self.data)
                return result
            except Exception as ex:
                tip = f'[{self.name}]fail to serializer {self.data}'
                logger.error(f'{tip},ex:{ex}\n{traceback.format_exc()}')
                self.data = {}
        return self.data or {}

    def from_dict(self, data: dict):
        if self.deserializer:
            try:
                self.data = self.deserializer(data)
            except Exception as ex:
                tip = f'[{self.name}]fail to deserializer {self.data}'
                logger.error(f'{tip},ex:{ex}\n{traceback.format_exc()}')
                self.data = {}
            return
        self.data = data or {}


DBS_DEBUG = False


class Database(ISaver):
    lock = threading.Lock()
    cache: dict[str, DatabaseData] = {}  # 通过DatabaseData[T]存储实现传地址
    # TODO 使用真实的传址
    root_path: str = None
    raw_value: dict
    '''数据原始对象'''
    database: str
    '''数据库名称'''

    def __init__(
            self,     database: str,
            serializer: callable = None, deserializer: callable = None,
            log: bool = True) -> None:
        self.log = log

        self.database = database
        self.data_obj = DatabaseData(
            None, serializer, deserializer, name=database)

        self.load_db()

    def check_file(self):
        return Database.ensure_file(self.database_filename, log=self.log)

    @staticmethod
    def ensure_file(path: str, log: bool = True):
        xxx = pathlib2.Path(path)
        if not xxx.parent.is_dir():
            t_path = xxx.parent.as_posix()
            if log:
                logger.warning(f'target-db-path not exist,create:{t_path}')
            os.makedirs(t_path)
        if not xxx.exists():
            t_file = xxx.as_posix()
            if log:
                logger.warning(f'target-db-file not exist,create:{t_file}')
            with open(t_file, 'w'):
                pass

    def load_db(self, reload: bool = False):
        with Database.lock:
            if not reload:
                if prev := Database.cache.get(self.database):
                    # 覆盖为缓存
                    self.data_obj = prev
                    return self.value

            if self.log:
                pre = 'new database cache is loaded:'
                suf = f',id:{hex(id(self.data_obj))}'
                debug_func = logger.debug if reload else logger.warning
                debug_func(f'{pre}{self.database_filename}{suf}')
            self.check_file()
            with open(self.database_filename, 'r', encoding='utf-8') as f:
                data = f.read()
                if len(data) < 3:
                    data = '{}'
                self.data_obj.from_dict(json.loads(data))

            Database.cache[self.database] = self.data_obj
            return self.value

    def save(self):
        if hasattr(self, 'is_deleted'):
            return False
        if Database.cache.get(self.database) is None:
            return  # 已被删除
        data = self.data_obj.to_dict()
        return Database.save_direct(self.database_filename, data)

    @staticmethod
    def save_direct(path: str, data: dict):
        try:
            if data is not None:
                x = isinstance(data, dict) or isinstance(data, list)
                assert x, f'无效的类型:{type(data)}{data}'

            Database.ensure_file(path)
            Database.ensure_key_is_str(path, data)
            with open(path, 'w', encoding='utf-8') as f:
                # print(f'{path}:type{type(data)},keys:{len(data)},')
                data_raw = json.dumps(
                    data, cls=DateEncoder, ensure_ascii=False)
                if DBS_DEBUG:
                    print('save_direct', path, len(data_raw))
                f.write(data_raw)
        except Exception as ex:
            tip = f'file-db:fail on save_direct {path}：'
            logger.error(f'{tip},ex:{ex}\n{traceback.format_exc()}')
            return False
        return True

    @staticmethod
    def ensure_key_is_str(name: str, data: dict):
        if isinstance(data, dict):
            for x in data:
                if isinstance(x, str):
                    continue
                logger.warning(f'{name},key [{x}] invalid type:{type(x)}')
                # 此处不要尝试修复，因为可能会有重复key导致数据丢失

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
        return Database.cache.get(self.database).data

    @value.setter
    def value(self, value: any) -> dict:
        if not Database.cache.get(self.database):
            Database.cache[self.database] = self.data_obj
        Database.cache[self.database].data = value

    def get(self, key: str, default: any = None):
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
        stacks = str.join('\n', [str(x) for x in traceback.extract_stack()])
        print(f'attempt to save all from {stacks}')
        count_all = len(Database.cache)
        count_succ = 0
        for x in Database.cache:
            data_obj = Database.cache[x]
            path = Database._database_filename(x)
            r = Database.save_direct(path, data_obj.to_dict())
            if r:
                count_succ += 1
        print(f'completed save all:{count_succ}/{count_all}')

    def delete(self):
        logger.warning(f'attempt to delete db:{self.database}')
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
# should let user manually run instead of auto
# because here shall cause data-lost
# why? seeems register let static-class to be a new instances.
# atexit.register(Database.save_all)
