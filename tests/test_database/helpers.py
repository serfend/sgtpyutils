"""helpers.py — 供 test_database 包内各模块共享的辅助函数。"""

import asyncio
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# 事件循环延迟测量（检测持续阻塞，而非单次峰值）
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
    consecutive_threshold: int = 5,
) -> tuple[bool, float, float, int]:
    """并发运行 slow_coro 和延迟测量，返回 (通过?, 最大间隔, 平均间隔, 持续阻塞次数)。

    阻塞检测策略（严格）：
    - 单次峰值 > max_allowed_latency：警告（Windows 调度偶尔会有）
    - 连续 consecutive_threshold 个间隔都 > max_allowed_latency：失败（持续阻塞）

    这样既能检测真正的阻塞（持续占用事件循环），
    又不会因为 Windows 调度的一次峰值误报。

    Args:
        slow_coro: 模拟慢 I/O 的协程（会与测量并发执行）
        during: 测量持续时间（秒）
        interval: 测量间隔（秒）
        max_allowed_latency: 允许的最大间隔（秒），超过则记录为"阻塞采样"
        consecutive_threshold: 连续多少个阻塞采样才判定为"持续阻塞"（默认 5）

    Returns:
        (passed, max_latency, avg_latency, blocking_events)
        - passed: 是否通过（无持续阻塞）
        - max_latency: 最大间隔（秒）
        - avg_latency: 平均间隔（秒）
        - blocking_events: 持续阻塞事件数（连续 N 个间隔超标的次数）
    """
    latencies: list[float] = []

    async def run_slow():
        await slow_coro

    async def run_measure():
        nonlocal latencies
        latencies = await measure_event_loop_latency(during, interval)

    await asyncio.gather(run_slow(), run_measure())

    if not latencies:
        return True, 0.0, 0.0, 0

    max_lat = max(latencies)
    avg_lat = sum(latencies) / len(latencies)

    # 检测持续阻塞：连续 consecutive_threshold 个间隔都超标
    consecutive_count = 0
    max_consecutive = 0
    blocking_events = 0
    for lat in latencies:
        if lat > max_allowed_latency:
            consecutive_count += 1
            if consecutive_count >= consecutive_threshold:
                blocking_events += 1
                consecutive_count = 0  # 重置，开始检测下一次持续阻塞
        else:
            consecutive_count = 0
        max_consecutive = max(max_consecutive, consecutive_count)

    # 通过条件：无持续阻塞事件
    passed = blocking_events == 0

    return passed, max_lat, avg_lat, blocking_events


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
