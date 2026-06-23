"""helpers.py — 供 test_database 包内各模块共享的辅助函数。"""

import asyncio
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# 事件循环延迟测量
# ---------------------------------------------------------------------------

async def measure_event_loop_latency(
    during: float,
    interval: float = 0.01,
) -> list[float]:
    """在 during 秒内每 interval 秒采样一次，返回每次采样之间的实际时间间隔。

    如果事件循环被阻塞，某些间隔会显著大于 interval。
    """
    times: list[float] = []
    loop = asyncio.get_event_loop()
    start = loop.time()
    next_time = start

    while True:
        now = loop.time()
        times.append(now)
        next_time += interval
        if next_time <= now:
            pass  # 已经落后，不 sleep，直接继续
        else:
            await asyncio.sleep(next_time - now)
        if loop.time() - start >= during:
            break

    return [times[i + 1] - times[i] for i in range(len(times) - 1)]


async def run_blocking_test(
    slow_coro,
    during: float = 2.0,
    interval: float = 0.01,
    max_allowed_latency: float = 0.05,
) -> tuple[bool, float, float]:
    """并发运行 slow_coro 和延迟测量，返回 (通过?, 最大间隔, 平均间隔)。

    slow_coro: 模拟慢 I/O 的协程（会与测量并发执行）
    during: 测量持续时间（秒）
    interval: 测量间隔（秒）
    max_allowed_latency: 允许的最大间隔（秒），超过则认为有阻塞
    """
    latencies: list[float] = []

    async def run_slow():
        await slow_coro

    async def run_measure():
        nonlocal latencies
        latencies = await measure_event_loop_latency(during, interval)

    await asyncio.gather(run_slow(), run_measure())

    if not latencies:
        return False, 0.0, 0.0

    max_lat = max(latencies)
    avg_lat = sum(latencies) / len(latencies)
    passed = max_lat < max_allowed_latency
    return passed, max_lat, avg_lat


# ---------------------------------------------------------------------------
# 通用 mock 工具
# ---------------------------------------------------------------------------

def mock_slow_io(has_aiofiles: bool, io_type: str = "write", delay: float = 1.0):
    """返回一个适用于 patch 的 side_effect / wrapper，模拟慢 I/O。

    has_aiofiles: 是否安装了 aiofiles
    io_type: "write" | "read"
    delay: 模拟延迟（秒）
    """
    import pathlib
    import unittest.mock

    if has_aiofiles:
        # aiofiles 路径：用 asyncio.sleep 模拟慢 I/O（不阻塞 event loop）
        if io_type == "write":
            async def slow_save(path, data):
                await asyncio.sleep(delay)
                return True
            return slow_save
        else:
            async def slow_load(path):
                await asyncio.sleep(delay)
                return '{"x": 1}'
            return slow_load
    else:
        # run_in_executor 路径：让线程池里的同步调用变慢
        if io_type == "write":
            def slow_write_text(self, data, encoding):
                time.sleep(delay)
            return slow_write_text
        else:
            def slow_read_text(self, encoding):
                time.sleep(delay)
                return '{"x": 1}'
            return slow_read_text
