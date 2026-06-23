"""底层 I/O 工具函数（同步/异步）。

供 Database 类内部调用，也可通过 Database.save_direct / Database.ensure_file 公开访问。

I/O 策略：
- 优先使用 orjson（Rust 实现，释放 GIL，不阻塞事件循环）
- 未安装 orjson 时降级为 json.dumps（此时大文件会持有 GIL，可能阻塞事件循环）
- 所有 I/O 均通过 run_in_executor 在线程池执行
"""

import asyncio
import json as _std_json
import traceback
from pathlib import Path
from typing import Any, Generator

from sgtpyutils.datetime import DateTime
from sgtpyutils.logger import logger

from .models import DateEncoder


# ------------------------------------------------------------------
# orjson 软依赖：Rust 实现，释放 GIL，小文件推荐
# 大文件（>100MB）建议用流式写入（见 _streaming_json_dumps）
# ------------------------------------------------------------------


def _orjson_default(obj: Any) -> Any:
    """orjson 的 default 函数，等价于 DateEncoder。"""
    if isinstance(obj, DateTime):
        return obj.tostring()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


try:
    import orjson as _json_lib

    def _json_dumps(data: Any) -> bytes:
        return _json_lib.dumps(data, default=_orjson_default)

    def _json_loads(raw: str | bytes) -> Any:
        return _json_lib.loads(raw)

    HAS_ORJSON = True
except ImportError:
    import json as _json_lib

    def _json_dumps(data: Any) -> str:
        return _json_lib.dumps(data, cls=DateEncoder, ensure_ascii=False)

    def _json_loads(raw: str | bytes) -> Any:
        return _json_lib.loads(raw)

    HAS_ORJSON = False


# ------------------------------------------------------------------
# 流式 JSON 序列化（支持超大文件，峰值内存低）
# ------------------------------------------------------------------


def _streaming_json_dumps(
    data: Any, chunk_size: int = 64 * 1024
) -> Generator[str, None, None]:
    """流式 JSON 序列化，逐块产生 JSON 字符串。

    使用 json.JSONEncoder().iterencode() 实现，每次 yield 一个片段。
    峰值内存只取决于单条记录大小，而非整个文件。

    Args:
        data: 要序列化的数据（dict / list）
        chunk_size: 每轮累积的字符数上限（默认 64KB）

    Yields:
        str: JSON 字符串片段
    """
    import json as _json

    encoder = _json.JSONEncoder(ensure_ascii=False, default=_date_encoder_default)
    # iterencode 返回一个 generator，逐块产生 JSON 字符串
    # 但 iterencode 的 chunk 很小（通常几个字符），需要累积到 chunk_size 再 yield
    # 不过 iterencode 本身已经是流式了，直接 yield 每个片段也可以
    # 为了更少次数的 write() 调用，这里累积一下
    buf = []
    buf_len = 0
    for chunk in encoder.iterencode(data):
        buf.append(chunk)
        buf_len += len(chunk)
        if buf_len >= chunk_size:
            yield "".join(buf)
            buf = []
            buf_len = 0
    if buf:
        yield "".join(buf)


def _date_encoder_default(obj: Any) -> Any:
    """json.JSONEncoder 的 default 函数，处理 DateTime。"""
    if isinstance(obj, DateTime):
        return obj.tostring()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


async def save_direct_async_streaming(
    path: str | Path, data: Any, chunk_size: int = 1024 * 1024
) -> bool:
    """流式异步保存大文件（峰值内存低，适合 100MB+ 文件）。

    与 save_direct_async 的区别：
    - 使用 json.JSONEncoder().iterencode() 流式序列化
    - 配合文件流式写入，峰值内存 ~chunk_size（默认 1024KB）
    - 速度比 orjson 慢，但内存占用极低

    Args:
        path: 文件路径
        data: 要保存的数据
        chunk_size: 每次写入的字符数上限（默认 1024KB）
    """
    try:
        if data is not None:
            assert isinstance(data, (dict, list)), f"无效的类型: {type(data)}"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _ensure_file_sync, path, True)

        def _do_streaming_write() -> None:
            _ensure_key_is_str(path, data)
            p = Path(path)
            # 用 'w' 模式打开，逐块写入
            with open(p, "w", encoding="utf-8") as f:
                for chunk in _streaming_json_dumps(data, chunk_size):
                    f.write(chunk)
                    # 让出 CPU（如果 chunk 很大，可以在这里 yield）
                    # 但在 executor 线程里无法 asyncio.sleep，所以不处理

        await loop.run_in_executor(None, _do_streaming_write)
        return True
    except Exception as ex:
        logger.error(
            f"file-db: fail on streaming_save_direct_async {path}: "
            f"ex:{ex}\n{traceback.format_exc()}"
        )
        return False


# ------------------------------------------------------------------
# 文件确保存在
# ------------------------------------------------------------------


def _ensure_file_sync(path: str | Path, log: bool = False) -> None:
    p = Path(path)
    if not p.exists():
        if log:
            logger.warning(f"target-db-file not exist, create: {p}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()


async def _ensure_file_async(path: str | Path, log: bool = False) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _ensure_file_sync, path, log)


def ensure_file(path: str | Path, log: bool = False) -> None:
    _ensure_file_sync(path, log)


async def ensure_file_async(path: str | Path, log: bool = False) -> None:
    await _ensure_file_async(path, log)


# ------------------------------------------------------------------
# 同步保存 / 加载
# ------------------------------------------------------------------


def save_direct(path: str | Path, data: Any) -> bool:
    """同步保存数据到文件。"""
    try:
        if data is not None:
            assert isinstance(data, (dict, list)), f"无效的类型: {type(data)}"

        _ensure_file_sync(path, True)
        _ensure_key_is_str(path, data)
        raw = _json_dumps(data)
        if isinstance(raw, bytes):
            Path(path).write_bytes(raw)
        else:
            Path(path).write_text(raw, encoding="utf-8")
        return True
    except Exception as ex:
        logger.error(
            f"file-db: fail on save_direct {path}: ex:{ex}\n{traceback.format_exc()}"
        )
        return False


async def save_direct_async(path: str | Path, data: Any) -> bool:
    """异步保存数据到文件。

    所有 I/O 和 CPU 密集操作（_json_dumps）均在线程池中执行，
    保证事件循环不被阻塞。
    """
    try:
        if data is not None:
            assert isinstance(data, (dict, list)), f"无效的类型: {type(data)}"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _ensure_file_sync, path, True)

        def _do_write() -> None:
            _ensure_key_is_str(path, data)
            raw = _json_dumps(data)
            if isinstance(raw, bytes):
                Path(path).write_bytes(raw)
            else:
                Path(path).write_text(raw, encoding="utf-8")

        await loop.run_in_executor(None, _do_write)
        return True
    except Exception as ex:
        logger.error(
            f"file-db: fail on save_direct_async {path}: "
            f"ex:{ex}\n{traceback.format_exc()}"
        )
        return False


async def load_direct_async(path: str | Path) -> Any:
    """异步读取文件内容。

    文件读取和 json.loads 均在线程池中执行，保证事件循环不被阻塞。
    """
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(
        None,
        lambda: Path(path).read_bytes()
        if HAS_ORJSON
        else Path(path).read_text(encoding="utf-8"),
    )
    data = await loop.run_in_executor(None, _json_loads, raw)
    return data


# ------------------------------------------------------------------
# 内部校验
# ------------------------------------------------------------------


def _ensure_key_is_str(name: str, data: Any) -> None:
    if isinstance(data, dict):
        for k in data:
            if not isinstance(k, str):
                logger.warning(f"{name}, key [{k}] invalid type: {type(k)}")
