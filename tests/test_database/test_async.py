"""异步 I/O 测试（save / load / delete 的 async 路径）。"""

import asyncio
import os
import tempfile
import json as json_mod
from pathlib import Path

from sgtpyutils.database import filebase_database
from sgtpyutils.database.filebase_database import io_utils


# ---------------------------------------------------------------------------
# save_async
# ---------------------------------------------------------------------------

def test_save_async():
    db = filebase_database.Database('test_async')
    db.value['async_key'] = 'async_val'
    result = asyncio.run(db.save_async())
    assert result is True

    db2 = filebase_database.Database('test_async')
    assert db2.value['async_key'] == 'async_val'
    db2.delete()


def test_save_async_when_deleted():
    """_is_deleted=True 时 save_async 返回 False"""
    db = filebase_database.Database('test_async_deleted')
    db.value['x'] = 1
    db.save()
    asyncio.run(db.delete_async())
    result = asyncio.run(db.save_async())
    assert result is False


def test_save_async_not_in_cache():
    """不在缓存中时 save_async 返回 False"""
    db = filebase_database.Database('test_async_no_cache')
    db.value['x'] = 1
    db.save()
    filebase_database.Database.cache.pop('test_async_no_cache', None)
    result = asyncio.run(db.save_async())
    assert result is False
    db2 = filebase_database.Database('test_async_no_cache')
    db2.delete()


# ---------------------------------------------------------------------------
# save_all_async
# ---------------------------------------------------------------------------

def test_save_all_async():
    """测试 save_all_async 并发保存多个数据库"""
    names = [f'test_save_all_async_{i}' for i in range(5)]
    for name in names:
        db = filebase_database.Database(name)
        db.value['x'] = name

    count_succ, count_all = asyncio.run(filebase_database.Database.save_all_async())
    assert count_succ == count_all == 5

    for name in names:
        db = filebase_database.Database(name)
        assert db.value['x'] == name
        db.delete()


def test_save_all_async_empty_cache():
    """缓存为空时 save_all_async 返回 (0, 0)"""
    filebase_database.Database.cache.clear()
    result = asyncio.run(filebase_database.Database.save_all_async())
    assert result == (0, 0)


# ---------------------------------------------------------------------------
# load_db_async
# ---------------------------------------------------------------------------

def test_load_db_async():
    """测试 load_db_async 异步加载"""
    db = filebase_database.Database('test_load_async')
    db.value['key'] = 'value'
    db.save()

    filebase_database.Database.cache = {}

    db2 = filebase_database.Database('test_load_async')
    result = asyncio.run(db2.load_db_async())
    assert result['key'] == 'value'
    db2.delete()


def test_load_db_async_reload():
    """测试 load_db_async(reload=True) 强制重新从磁盘加载"""
    db = filebase_database.Database('test_load_reload')
    db.value['v'] = 'v1'
    db.save()

    raw = json_mod.loads(Path(db.database_filename).read_text(encoding='utf-8'))
    raw['v'] = 'v2'
    Path(db.database_filename).write_text(
        json_mod.dumps(raw, ensure_ascii=False), encoding='utf-8'
    )

    db2 = filebase_database.Database('test_load_reload')
    assert db2.value['v'] == 'v1'

    result = asyncio.run(db2.load_db_async(reload=True))
    assert result['v'] == 'v2'

    db2.delete()


# ---------------------------------------------------------------------------
# delete_async
# ---------------------------------------------------------------------------

def test_delete_async():
    db = filebase_database.Database('test_delete_async')
    db.value['key'] = 'value'
    db.save()
    assert os.path.exists(db.database_filename)

    asyncio.run(db.delete_async())
    assert not os.path.exists(db.database_filename)


def test_delete_async_file_not_exist():
    """测试 delete_async 当文件不存在时不报错"""
    db = filebase_database.Database('test_delete_async_no_file')
    db.value['x'] = 1
    db.save()
    assert os.path.exists(db.database_filename)

    os.unlink(db.database_filename)
    asyncio.run(db.delete_async())
    assert db._is_deleted is True


# ---------------------------------------------------------------------------
# save_direct_async / ensure_file_async
# ---------------------------------------------------------------------------

def test_save_direct_async():
    """测试 save_direct_async 静态方法"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        tmp_path = f.name
        json_mod.dump({'test': 'initial'}, f)

    try:
        result = asyncio.run(
            filebase_database.Database.save_direct_async(tmp_path, {'test': 'async_value'})
        )
        assert result is True

        with open(tmp_path, 'r', encoding='utf-8') as f:
            data = json_mod.load(f)
            assert data['test'] == 'async_value'
    finally:
        os.unlink(tmp_path)


def test_save_direct_async_invalid_type():
    """save_direct_async 传入非法类型应返回 False"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        tmp_path = f.name

    try:
        result = asyncio.run(
            filebase_database.Database.save_direct_async(tmp_path, 'invalid_type')
        )
        assert result is False
    finally:
        os.unlink(tmp_path)


def test_ensure_file_async():
    """测试 ensure_file_async 异步创建文件"""
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, 'subdir', 'test_async.json')

    assert not os.path.exists(tmp_path)
    asyncio.run(filebase_database.Database.ensure_file_async(tmp_path))
    assert os.path.exists(tmp_path)

    asyncio.run(filebase_database.Database.ensure_file_async(tmp_path))
    assert os.path.exists(tmp_path)

    # 清理
    try:
        os.rmdir(os.path.join(tmp_dir, 'subdir'))
        os.rmdir(tmp_dir)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# save_async_streaming
# ---------------------------------------------------------------------------

def test_save_async_streaming():
    """测试 save_async_streaming 方法（流式写入，峰值内存低）"""
    db_name = 'test_streaming'
    db = filebase_database.Database(db_name)
    db.value = {'key': 'value', 'num': 42, 'list': [1, 2, 3]}

    asyncio.run(db.save_async_streaming())
    assert os.path.exists(db.database_filename)

    # 验证文件内容正确
    db2 = filebase_database.Database(db_name)
    asyncio.run(db2.load_db_async())
    assert db2.value['key'] == 'value'
    assert db2.value['num'] == 42
    assert db2.value['list'] == [1, 2, 3]

    db2.delete()


def test_save_async_streaming_when_deleted():
    """测试 save_async_streaming 当 _is_deleted=True 时返回 False"""
    db = filebase_database.Database('test_streaming_deleted')
    db.delete()
    result = asyncio.run(db.save_async_streaming())
    assert result is False


def test_save_direct_async_streaming():
    """测试 save_direct_async_streaming 静态方法"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        tmp_path = f.name
        json_mod.dump({'test': 'initial'}, f)

    try:
        result = asyncio.run(
            filebase_database.save_direct_async_streaming(tmp_path, {'test': 'streaming_value'})
        )
        assert result is True

        with open(tmp_path, 'r', encoding='utf-8') as f:
            data = json_mod.load(f)
            assert data['test'] == 'streaming_value'
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass  # 文件可能已被删除
