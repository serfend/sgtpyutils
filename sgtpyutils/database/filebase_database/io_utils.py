"""底层 I/O 工具函数（同步/异步）。

供 Database 类内部调用，也可通过 Database.save_direct / Database.ensure_file 公开访问。

异步 I/O 统一使用 run_in_executor（线程池），保证事件循环不被阻塞。
不依赖 aiofiles，避免软依赖带来的不确定性。
"""

import asyncio
import json
import traceback
from pathlib import Path
from typing import Any

from sgtpyutils.logger import logger

from .models import DateEncoder


# ------------------------------------------------------------------
# 文件确保存在
# ------------------------------------------------------------------

def _ensure_file_sync(path: str | Path, log: bool = True) -> None:
    """同步确保文件存在（目录 + 空文件）。"""
    p = Path(path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        if log:
            logger.warning(f'target-db-path not exist, create: {p.parent}')
    if not p.exists():
        if log:
            logger.warning(f'target-db-file not exist, create: {p}')
        p.touch()


async def _ensure_file_async(path: str | Path, log: bool = True) -> None:
    """异步确保文件存在。I/O 通过 run_in_executor 执行。"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _ensure_file_sync, path, log)


def ensure_file(path: str | Path, log: bool = True) -> None:
    """公开 API：同步确保文件存在。"""
    _ensure_file_sync(path, log)


async def ensure_file_async(path: str | Path, log: bool = True) -> None:
    """公开 API：异步确保文件存在。"""
    await _ensure_file_async(path, log)


# ------------------------------------------------------------------
# 保存
# ------------------------------------------------------------------

def save_direct(path: str | Path, data: Any) -> bool:
    """同步保存数据到文件。"""
    try:
        if data is not None:
            assert isinstance(data, (dict, list)), f'无效的类型: {type(data)}'
        _ensure_file_sync(path)
        _ensure_key_is_str(path, data)
        raw = json.dumps(data, cls=DateEncoder, ensure_ascii=False)
        Path(path).write_text(raw, encoding='utf-8')
        return True
    except Exception as ex:
        logger.error(
            f'file-db: fail on save_direct {path}: '
            f'ex:{ex}\n{traceback.format_exc()}'
        )
        return False


async def save_direct_async(path: str | Path, data: Any) -> bool:
    """异步保存数据到文件。

    所有 I/O 和 CPU 密集操作（json.dumps）均在线程池中执行，
    保证事件循环不被阻塞。
    """
    try:
        if data is not None:
            assert isinstance(data, (dict, list)), f'无效的类型: {type(data)}'

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _ensure_file_sync, path, True)

        def _do_write() -> None:
            _ensure_key_is_str(path, data)
            raw = json.dumps(data, cls=DateEncoder, ensure_ascii=False)
            Path(path).write_text(raw, encoding='utf-8')

        await loop.run_in_executor(None, _do_write)
        return True
    except Exception as ex:
        logger.error(
            f'file-db: fail on save_direct_async {path}: '
            f'ex:{ex}\n{traceback.format_exc()}'
        )
        return False


async def load_direct_async(path: str | Path) -> str:
    """异步读取文件内容。

    文件读取在线程池中执行，保证事件循环不被阻塞。
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: Path(path).read_text(encoding='utf-8')
    )


# ------------------------------------------------------------------
# 内部校验
# ------------------------------------------------------------------

def _ensure_key_is_str(name: str, data: Any) -> None:
    if isinstance(data, dict):
        for k in data:
            if not isinstance(k, str):
                logger.warning(f'{name}, key [{k}] invalid type: {type(k)}')
