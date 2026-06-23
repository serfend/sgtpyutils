"""tests/test_database package.

拆分自 tests/test_database.py，按功能域组织：
- test_basic.py      — 基础 CRUD（同步路径）
- test_async.py       — 异步 I/O（save / load / delete 的 async 路径）
- test_concurrent.py  — 并发读写一致性
- test_blocking.py   — 事件循环阻塞检测
- helpers.py          — 公共辅助函数
"""
