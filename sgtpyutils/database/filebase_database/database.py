"""Database 主类 — 基于 JSON 文件的键值数据库，支持进程内缓存。"""

import asyncio
import json
import os
import threading
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from sgtpyutils.functools import AssignableArg
from sgtpyutils.logger import logger

from ..BaseSaver import ISaver
from .io_utils import (
    _ensure_file_sync,
    _ensure_file_async,
    save_direct,
    save_direct_async,
    ensure_file,
    ensure_file_async,
    _ensure_key_is_str,
)
from .models import DatabaseData, DateEncoder


class Database(ISaver):
    """基于 JSON 文件的键值数据库，支持进程内缓存。

    重构变更（vs 原版）:
    - 用 pathlib.Path 替代 pathlib2 / os.path
    - 异步方法统一使用 run_in_executor，移除对 aiofiles 的硬依赖
    - 添加 set_root_path() / get_root_path() 管理根路径
    - 日志统一使用 logger，移除 print
    - 保持公共 API 完全兼容（Database.cache / save_direct / ensure_file 等）
    """

    # 类级锁（同步 / 异步）
    lock: threading.Lock = threading.Lock()
    _async_lock: Optional[asyncio.Lock] = None

    # 全局缓存：database_name -> DatabaseData
    # 保留为公共类属性以保持向后兼容（测试直接访问 Database.cache）
    cache: dict[str, DatabaseData] = {}

    # 根路径（惰性初始化）
    _root_path: Optional[Path] = None

    def __init__(
        self,
        database: str,
        serializer: Optional[Callable] = None,
        deserializer: Optional[Callable] = None,
        log: bool = True,
    ):
        self._database = database
        self._log = log
        self._data_obj = DatabaseData(None, serializer, deserializer, name=database)
        self._base_path: Optional[Path] = None
        self._is_deleted: bool = False
        self.load_db()

    # ------------------------------------------------------------------
    # 类级配置
    # ------------------------------------------------------------------

    @classmethod
    def set_root_path(cls, path: str | Path) -> None:
        """设置数据库文件的根目录。应在创建任何 Database 实例前调用。"""
        cls._root_path = Path(path)

    @classmethod
    def get_root_path(cls) -> Path:
        """返回数据库根目录，惰性初始化为 <package>/database/。"""
        if cls._root_path is None:
            cls._root_path = Path(__file__).resolve().parent.parent.parent / 'database'
        return cls._root_path

    @classmethod
    def get_async_lock(cls) -> asyncio.Lock:
        if cls._async_lock is None:
            cls._async_lock = asyncio.Lock()
        return cls._async_lock

    # ------------------------------------------------------------------
    # 路径工具
    # ------------------------------------------------------------------

    @property
    def database_filename(self) -> str:
        return str(self.base_path / f'{self._database}.json')

    @property
    def base_path(self) -> Path:
        if self._base_path is None:
            db = self._database
            if Path(db).is_absolute():
                self._base_path = Path(db).parent
            else:
                self._base_path = self.get_root_path()
        return self._base_path

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------

    def load_db(self, reload: bool = False) -> dict:
        with Database.lock:
            if not reload:
                if prev := Database.cache.get(self._database):
                    self._data_obj = prev
                    return self.value

            if self._log:
                logger.info(
                    f'load database: {self.database_filename} '
                    f'(id:{hex(id(self._data_obj))})'
                )

            _ensure_file_sync(self.database_filename, log=self._log)
            raw = Path(self.database_filename).read_text(encoding='utf-8')
            if len(raw) < 3:
                raw = '{}'
            self._data_obj.from_dict(json.loads(raw))
            Database.cache[self._database] = self._data_obj
            return self.value

    async def load_db_async(self, reload: bool = False) -> dict:
        async with Database.get_async_lock():
            if not reload:
                if prev := Database.cache.get(self._database):
                    self._data_obj = prev
                    return self.value

            if self._log:
                logger.info(
                    f'load database(async): {self.database_filename} '
                    f'(id:{hex(id(self._data_obj))})'
                )

            await _ensure_file_async(self.database_filename, log=self._log)

            loop = asyncio.get_event_loop()
            raw: str = await loop.run_in_executor(
                None, lambda: Path(self.database_filename).read_text(encoding='utf-8')
            )
            if len(raw) < 3:
                raw = '{}'
            data = await loop.run_in_executor(None, json.loads, raw)
            self._data_obj.from_dict(data)
            Database.cache[self._database] = self._data_obj
            return self.value

    # ------------------------------------------------------------------
    # 保存（实例方法）
    # ------------------------------------------------------------------

    def save(self) -> bool:
        if self._is_deleted:
            return False
        if self._database not in Database.cache:
            return False
        data = self._data_obj.to_dict()
        return save_direct(self.database_filename, data)

    async def save_async(self) -> bool:
        if self._is_deleted:
            return False
        if self._database not in Database.cache:
            return False
        data = self._data_obj.to_dict()
        return await save_direct_async(self.database_filename, data)

    # ------------------------------------------------------------------
    # 批量保存
    # ------------------------------------------------------------------

    @classmethod
    def save_all(cls) -> tuple[int, int]:
        """保存所有缓存的数据库。返回 (成功数, 总数)。"""
        total = len(cls.cache)
        if total == 0:
            return 0, 0
        ok = 0
        for name, data_obj in list(cls.cache.items()):
            path = cls._build_filename(name)
            if save_direct(path, data_obj.to_dict()):
                ok += 1
        logger.info(f'save_all: {ok}/{total}')
        return ok, total

    @classmethod
    async def save_all_async(cls) -> tuple[int, int]:
        """并发保存所有缓存的数据库。返回 (成功数, 总数)。"""
        total = len(cls.cache)
        if total == 0:
            return 0, 0
        tasks = [
            save_direct_async(cls._build_filename(name), data_obj.to_dict())
            for name, data_obj in list(cls.cache.items())
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        ok = sum(1 for r in results if r is True)
        logger.info(f'save_all_async: {ok}/{total}')
        return ok, total

    # ------------------------------------------------------------------
    # 删除
    # ------------------------------------------------------------------

    def delete(self) -> None:
        logger.warning(f'delete db: {self._database}')
        self._is_deleted = True
        Database.cache.pop(self._database, None)
        path = Path(self.database_filename)
        if path.exists():
            path.unlink()

    async def delete_async(self) -> None:
        logger.warning(f'delete db(async): {self._database}')
        self._is_deleted = True
        Database.cache.pop(self._database, None)
        path = Path(self.database_filename)
        if path.exists():
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, path.unlink)

    # ------------------------------------------------------------------
    # 数据访问
    # ------------------------------------------------------------------

    @property
    def value(self) -> Any:
        obj = Database.cache.get(self._database)
        return obj.data if obj else None

    @value.setter
    def value(self, v: Any) -> None:
        if self._database not in Database.cache:
            Database.cache[self._database] = self._data_obj
        Database.cache[self._database].data = v

    @property
    def data_obj(self) -> DatabaseData:
        """返回内部 DatabaseData 对象（向后兼容测试中 id() 比较）。"""
        return self._data_obj

    def get(self, key: str, default: Any = None) -> Any:
        if not isinstance(self.value, dict):
            raise TypeError('get() requires dict-valued database')
        if key not in self.value:
            self.value[key] = default
        return self.value.get(key)

    # ------------------------------------------------------------------
    # 装饰器
    # ------------------------------------------------------------------

    @staticmethod
    def require_database(db_path: str):
        """装饰器：自动创建 Database 实例并注入到方法参数。"""
        def decorator(target_method: Callable):
            @wraps(target_method)
            def wrapper(*args, **kwargs):
                db = Database(db_path)
                arg = AssignableArg(args, kwargs, target_method)
                arg.assign_by_type(Database, db)
                return target_method(*arg.args, **arg.kwargs)
            return wrapper
        return decorator

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    @classmethod
    def _build_filename(cls, database: str) -> str:
        """根据 database 名称生成完整文件路径。"""
        if Path(database).is_absolute():
            return database if database.endswith('.json') else f'{database}.json'
        return str(cls.get_root_path() / f'{database}.json')


# ------------------------------------------------------------------
# 向后兼容：将 io_utils 中的函数挂到 Database 类上作为静态方法
# 这样 Database.save_direct(...) / Database.ensure_file(...) 等调用继续有效
# ------------------------------------------------------------------
Database.save_direct = staticmethod(save_direct)
Database.save_direct_async = staticmethod(save_direct_async)
Database.ensure_file = staticmethod(ensure_file)
Database.ensure_file_async = staticmethod(ensure_file_async)
