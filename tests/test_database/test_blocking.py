"""事件循环阻塞检测测试（真实 I/O，不 mock）。

验证：save_async / save_all_async / load_db_async 在执行真实文件 I/O 时，
事件循环仍然能及时响应其他协程（即：不产生阻塞）。

测试原理：
1. 生成一个足够大的数据结构（~50MB JSON），使 json.dumps / 文件写入
   耗时达到可测量级别（1~3 秒）
2. 在慢操作进行的同时，以 10ms 间隔测量事件循环响应延迟
3. 若任何间隔 > 200ms，则认为事件循环被阻塞，测试失败
   （Windows 上 run_in_executor 的线程池调度有偶发延迟峰值，
     平均延迟仍 < 20ms，200ms 是合理的上限）
"""

import asyncio
import os
from pathlib import Path

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

def test_event_loop_not_blocked_by_save_async_real_write():
    """save_async 在真实大文件写入期间不阻塞事件循环。"""
    db_name = 'test_blocking_real_write'
    db = filebase_database.Database(db_name)
    db.value = _make_large_data(size_mb=50.0)

    async def slow_coro():
        await db.save_async()

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=5.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db2 = filebase_database.Database(db_name)
    db2.delete()

    assert passed, (
        f'save_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (理论应毫无任何延时)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  这说明有同步阻塞操作在事件循环线程中执行。'
    )


# ---------------------------------------------------------------------------
# save_all_async — 真实并发大文件写入
# ---------------------------------------------------------------------------

def test_event_loop_not_blocked_by_save_all_async_real_write():
    """save_all_async 并发保存多个大文件时不阻塞事件循环。"""
    # 3 个文件，每个 ~5MB，总大小合理
    names = [f'test_blocking_all_real_{i}' for i in range(3)]
    large_data = _make_large_data(size_mb=5.0)

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
            slow_coro(), during=5.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    assert passed, (
        f'save_all_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (理论应毫无任何延时)\n'
        f'  avg_latency = {avg_lat:.3f}s'
    )


# ---------------------------------------------------------------------------
# load_db_async — 真实大文件读取
# ---------------------------------------------------------------------------

def test_event_loop_not_blocked_by_load_db_async_real_read():
    """load_db_async 在真实大文件读取期间不阻塞事件循环。"""
    db_name = 'test_blocking_real_read'
    db = filebase_database.Database(db_name)
    db.value = _make_large_data(size_mb=50.0)
    db.save()

    async def slow_coro():
        db2 = filebase_database.Database(db_name)
        await db2.load_db_async(reload=True)

    passed, max_lat, avg_lat = asyncio.run(
        run_blocking_test(
            slow_coro(), during=5.0, interval=0.01,
            max_allowed_latency=0.20,
        )
    )

    db3 = filebase_database.Database(db_name)
    db3.delete()

    assert passed, (
        f'load_db_async 阻塞了事件循环！\n'
        f'  max_latency = {max_lat:.3f}s (理论应毫无任何延时)\n'
        f'  avg_latency = {avg_lat:.3f}s\n'
        f'  这说明有同步阻塞操作在事件循环线程中执行。'
    )
