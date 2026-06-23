"""事件循环阻塞检测测试（真实 I/O，不 mock）。

验证：save_async / save_all_async / load_db_async 在执行真实文件 I/O 时，
事件循环仍然能及时响应其他协程（即：不产生阻塞）。

测试策略：
- 用 50MB 数据 × 5 次循环，总 I/O 量 ~250MB，足够触发线程池调度
- 在慢操作进行的同时，以 10ms 间隔测量事件循环响应延迟
- 若任何间隔 > 200ms，则认为事件循环被阻塞，测试失败
  （orjson 释放 GIL，线程池调度在 Windows 上偶发峰值 < 200ms 是合理的）
"""

import asyncio
import os
from pathlib import Path

import pytest

from sgtpyutils.database import filebase_database

from .helpers import run_blocking_test


# ---------------------------------------------------------------------------
# 大文件生成辅助
# ---------------------------------------------------------------------------

def _make_large_data(size_mb: float = 50.0) -> dict:
    """生成一个约 size_mb MB 的 dict，用于模拟大文件写入。

    返回 {f'k_{i}': 'x' * chunk_size, ...}
    每个 entry 约 1KB JSON 开销，目标 size_mb MB。
    """
    num_keys = int(size_mb * 1024)
    chunk_size = 500
    return {f'k_{i}': 'x' * chunk_size for i in range(num_keys)}


# ---------------------------------------------------------------------------
# 回归防护：确认测量方法本身能检测到同步阻塞
# ---------------------------------------------------------------------------

def test_blocking_detection_works():
    """验证测量方法本身能检测到同步阻塞（回归防护）。"""
    import time

    async def blocking_coro():
        await asyncio.sleep(0.01)
        time.sleep(1.0)
        await asyncio.sleep(0.01)

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            blocking_coro(), during=2.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )
    assert passed is False, f'应检测到阻塞，但 max_lat={max_lat:.3f}s'
    assert max_lat > 0.5, f'最大间隔应明显 > 0.5s，实际 {max_lat:.3f}s'


# ---------------------------------------------------------------------------
# save_async — 真实大文件写入，不 mock
# ---------------------------------------------------------------------------

@ pytest.mark.slow
def test_event_loop_not_blocked_by_save_async_real_write():
    """save_async 在真实大文件写入期间不阻塞事件循环。

    策略：50MB × 5 次循环，总 I/O ~250MB，足够测量线程池调度。
    """
    db_name = 'test_blocking_real_write'
    db = filebase_database.Database(db_name)
    large_data = _make_large_data(size_mb=50.0)
    db.value = large_data

    async def slow_coro():
        for _ in range(5):
            await db.save_async()

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=10.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db2 = filebase_database.Database(db_name)
    db2.delete()

    assert passed, (
        f'save_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (允许上限 0.20s)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  这说明有同步阻塞操作在事件循环线程中执行。'
    )


# ---------------------------------------------------------------------------
# save_all_async — 真实并发大文件写入
# ---------------------------------------------------------------------------

@ pytest.mark.slow
def test_event_loop_not_blocked_by_save_all_async_real_write():
    """save_all_async 并发保存多个大文件时不阻塞事件循环。

    策略：10 个文件 × 10MB，并发写入，测量事件循环延迟。
    """
    names = [f'test_blocking_all_real_{i}' for i in range(10)]
    large_data = _make_large_data(size_mb=10.0)

    async def slow_coro():
        for name in names:
            db = filebase_database.Database(name)
            db.value = large_data
        await filebase_database.Database.save_all_async()
        for name in names:
            db = filebase_database.Database(name)
            db.delete()

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=10.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    assert passed, (
        f'save_all_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (允许上限 0.20s)\n'
        f'  avg_latency = {avg_lat:.3f}s'
    )


# ---------------------------------------------------------------------------
# load_db_async — 真实大文件读取
# ---------------------------------------------------------------------------

@ pytest.mark.slow
def test_event_loop_not_blocked_by_load_db_async_real_read():
    """load_db_async 在真实大文件读取期间不阻塞事件循环。

    策略：50MB 文件 × 5 次读取，测量事件循环延迟。
    """
    db_name = 'test_blocking_real_read'
    db = filebase_database.Database(db_name)
    db.value = _make_large_data(size_mb=50.0)
    db.save()

    async def slow_coro():
        for _ in range(5):
            db2 = filebase_database.Database(db_name)
            await db2.load_db_async(reload=True)

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=10.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db3 = filebase_database.Database(db_name)
    db3.delete()

    assert passed, (
        f'load_db_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (允许上限 0.20s)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  这说明有同步阻塞操作在事件循环线程中执行。'
    )


# ---------------------------------------------------------------------------
# save_async_streaming — 流式写入大文件，不阻塞事件循环
# ---------------------------------------------------------------------------

@ pytest.mark.slow
def test_event_loop_not_blocked_by_save_async_streaming_real_write():
    """save_async_streaming 在真实大文件流式写入期间不阻塞事件循环。

    策略：
    - 单文件 200MB（比 1GB 快，但足够大以测试流式写入）
    - 流式写入峰值内存 ~64KB，不阻塞事件循环
    - 若需要测试 1GB 文件，可修改 size_mb 参数
    """
    db_name = 'test_blocking_streaming_real_write'
    db = filebase_database.Database(db_name)
    # 200MB 文件，足够测试流式写入的内存优势
    large_data = _make_large_data(size_mb=200.0)
    db.value = large_data

    async def slow_coro():
        await db.save_async_streaming()

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=15.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db2 = filebase_database.Database(db_name)
    try:
        db2.delete()
    except Exception:
        pass

    assert passed, (
        f'save_async_streaming 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (允许上限 0.20s)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  流式写入应在 executor 线程中执行，不应阻塞事件循环。'
    )


@ pytest.mark.slow
def test_event_loop_not_blocked_by_save_async_streaming_1gb():
    """save_async_streaming 在 1GB 单文件写入期间不阻塞事件循环。

    这是针对高性能库的真实场景测试：
    - 单文件 1GB
    - 流式写入峰值内存 ~64KB（vs 普通写入 ~1GB+）
    - 事件循环延迟应 < 200ms
    """
    db_name = 'test_blocking_streaming_1gb'
    db = filebase_database.Database(db_name)
    # 1GB 文件
    large_data = _make_large_data(size_mb=1024.0)
    db.value = large_data

    async def slow_coro():
        await db.save_async_streaming()

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=30.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db2 = filebase_database.Database(db_name)
    try:
        db2.delete()
    except Exception:
        pass

    assert passed, (
        f'save_async_streaming (1GB) 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (允许上限 0.20s)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  1GB 文件流式写入不应阻塞事件循环。'
    )
