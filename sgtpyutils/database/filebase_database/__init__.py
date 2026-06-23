"""filebase_database 包入口。

向后兼容：
    from sgtpyutils.database.filebase_database import Database
    Database.cache / Database.save_direct / ... 均保持可用
"""

from pathlib import Path

from .database import Database
from .io_utils import save_direct, save_direct_async, save_direct_async_chunked, ensure_file, ensure_file_async
from .models import DatabaseData, DateEncoder

__all__ = [
    'Database',
    'DatabaseData',
    'DateEncoder',
    'save_direct',
    'save_direct_async',
    'save_direct_async_chunked',
    'ensure_file',
    'ensure_file_async',
]

# 初始化默认 root_path（兼容原代码末尾的赋值）
_DefaultRoot = Path(__file__).resolve().parent.parent.parent / 'database'
Database.set_root_path(_DefaultRoot)
