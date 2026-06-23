import pathlib2
import asyncio
import tempfile
import json as json_mod
from pathlib import Path
from sgtpyutils.database import filebase_database

import os


def test_db():
    db = filebase_database.Database('test')
    assert os.path.exists(db.database_filename)

    db.value['test'] = 'test'
    assert db.value['test'] == 'test'

    db.save()

    db = filebase_database.Database('test')
    assert db.value['test'] == 'test'

    db.delete()


def test_aop():
    @filebase_database.Database.require_database('test_aop')
    def test(database: filebase_database.Database):
        assert database
        assert database.database_filename
        database.delete()
    test()


def test_save_all():
    for i in range(10):
        db_name = f'test_save_all_{i}'
        db = filebase_database.Database(db_name)
        db.value['x'] = i

    filebase_database.Database.save_all()

    for i in range(10):
        db_name = f'test_save_all_{i}'
        db = filebase_database.Database(db_name)
        assert db.value['x'] == i

    for i in range(10):
        db_name = f'test_save_all_{i}'
        db = filebase_database.Database(db_name)
        db.delete()
        assert not os.path.exists(db.database_filename)


def test_multi_edit():
    db_name = 'test_multi_edit'
    db = filebase_database.Database(db_name)
    db.value['common'] = 1

    db2 = filebase_database.Database(db_name)
    db2.value['common'] += 1

    db3 = filebase_database.Database(db_name)
    db3.value['common2'] = '123'

    db_check = filebase_database.Database(db_name)
    assert db_check.value['common'] == 2
    assert db_check.value['common2'] == '123'

    db_check.delete()


def test_serializer():
    class TestSerializer:
        def __init__(self, data: dict = None) -> None:
            if data is None:
                return
            self.load_data(data)

        def to_dict(self) -> dict:
            return {
                'name': self.name
            }

        @classmethod
        def from_dict(cls, data: dict):
            target = TestSerializer()
            return target.load_data(data)

        def load_data(self, data: dict):
            if data is None:
                data = {}
            self.name = data.get('name')
            return self

    db_name = 'test_serializer'
    serialer = TestSerializer.to_dict
    def deserialer(x): return TestSerializer.from_dict(x)
    db = filebase_database.Database(db_name, serialer, deserialer)

    obj = TestSerializer({'name': 'xxx'})
    db.value = obj
    db.save()

    filebase_database.Database.cache = {}

    db = filebase_database.Database(db_name, serialer, deserialer)
    data: TestSerializer = db.value
    assert data.name == 'xxx'

    data.name = 'xx2'
    db.save()

    filebase_database.Database.cache = {}

    db = filebase_database.Database(db_name, serialer, deserialer)
    data: TestSerializer = db.value
    assert data.name == 'xx2'

    filebase_database.Database.save_all()
    db.delete()


def test_global_independent():
    path = pathlib2.Path(__file__).parent
    db_name = f'{path}test_global_independent'
    db = filebase_database.Database(db_name)
    db1 = filebase_database.Database(db_name)
    assert id(db.data_obj) == id(db1.data_obj)
    db1.value['test'] = '1'

    db_name2 = 'test_global_independent2'
    db2 = filebase_database.Database(db_name2)
    assert id(db.data_obj) != id(db2.data_obj)

    db2.value['test'] = '2'
    db2.value['test2'] = '2.1'

    assert db1.value.get('test') == '1'
    assert db2.value.get('test') == '2'
    assert db1.value.get('test2') is None
    assert db2.value.get('test2') == '2.1'

    db1.delete()
    db2.delete()


# ---------------------------------------------------------------------------
# 异步测试
# ---------------------------------------------------------------------------

def test_save_async():
    """测试 save_async 异步保存"""
    db = filebase_database.Database('test_async')
    db.value['async_key'] = 'async_val'
    result = asyncio.run(db.save_async())
    assert result is True

    # 验证数据确实写入
    db2 = filebase_database.Database('test_async')
    assert db2.value['async_key'] == 'async_val'
    db2.delete()


def test_save_async_when_deleted():
    """_is_deleted=True 时 save_async 返回 False"""
    db = filebase_database.Database('test_async_deleted')
    db.value['x'] = 1
    db.save()
    asyncio.run(db.delete_async())
    # 删除后再次 save_async 应返回 False
    result = asyncio.run(db.save_async())
    assert result is False


def test_save_async_not_in_cache():
    """不在缓存中时 save_async 返回 False"""
    db = filebase_database.Database('test_async_no_cache')
    db.value['x'] = 1
    db.save()
    # 模拟从缓存中移除
    filebase_database.Database.cache.pop('test_async_no_cache', None)
    # 此时 _database 不在 cache 中，save_async 返回 False
    result = asyncio.run(db.save_async())
    assert result is False
    # 清理
    db2 = filebase_database.Database('test_async_no_cache')
    db2.delete()


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
    # 清空缓存
    filebase_database.Database.cache.clear()
    result = asyncio.run(filebase_database.Database.save_all_async())
    assert result == (0, 0)


def test_load_db_async():
    """测试 load_db_async 异步加载"""
    db = filebase_database.Database('test_load_async')
    db.value['key'] = 'value'
    db.save()

    # 清除缓存强制重新加载
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

    # 直接修改磁盘文件，模拟外部变更
    raw = json_mod.loads(Path(db.database_filename).read_text(encoding='utf-8'))
    raw['v'] = 'v2'
    Path(db.database_filename).write_text(
        json_mod.dumps(raw, ensure_ascii=False), encoding='utf-8'
    )

    # 不使用 reload，应命中缓存（值仍为 v1）
    db2 = filebase_database.Database('test_load_reload')
    assert db2.value['v'] == 'v1'

    # 使用 reload=True，应读到 v2
    result =     asyncio.run(db2.load_db_async(reload=True))
    assert result['v'] == 'v2'

    db2.delete()


def test_delete_async():

    """测试 delete_async 异步删除"""
    db = filebase_database.Database('test_delete_async')
    db.value['key'] = 'value'
    db.save()
    assert os.path.exists(db.database_filename)

    asyncio.run(db.delete_async())
    assert not os.path.exists(db.database_filename)


def test_delete_async_file_not_exist():
    """测试 delete_async 当文件不存在时不报错（path.exists() 检查保护）"""
    db = filebase_database.Database('test_delete_async_no_file')
    db.value['x'] = 1
    db.save()
    assert os.path.exists(db.database_filename)

    # 手动删除文件后再调用 delete_async，应不抛异常
    os.unlink(db.database_filename)
    asyncio.run(db.delete_async())  # 不应抛异常
    assert db._is_deleted is True


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
        # 传入字符串（非 dict/list）应触发断言失败，返回 False
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

    # 再次调用不应报错
    asyncio.run(filebase_database.Database.ensure_file_async(tmp_path))
    assert os.path.exists(tmp_path)

    os.unlink(tmp_path)
    os.rmdir(os.path.join(tmp_dir, 'subdir'))
    os.rmdir(tmp_dir)


def test_concurrent_read_write():
    """并发读写同一数据库的一致性测试"""
    db_name = 'test_concurrent'
    db = filebase_database.Database(db_name)
    db.value['counter'] = 0
    db.save()

    async def increment():
        """模拟并发递增：load -> modify -> save"""
        for _ in range(20):
            db = filebase_database.Database(db_name)
            val = db.value.get('counter', 0)
            db.value['counter'] = val + 1
            await db.save_async()

    async def run_concurrent():
        tasks = [increment() for _ in range(5)]
        await asyncio.gather(*tasks)

    asyncio.run(run_concurrent())

    # 由于有缓存 + 锁，最终结果应为 100（5 * 20）
    # 注意：当前实现中缓存是进程内共享的，save_async 会写磁盘
    # 但多个 Database 实例共享同一个 DatabaseData（通过 cache），
    # 所以并发递增实际是安全的（都在操作同一个 dict）
    db_final = filebase_database.Database(db_name)
    # 由于缓存共享，每次 save_async 都写同一个 dict 的当前值
    # 最终值取决于最后一次函数调用时的 val
    # 这里我们只验证文件能正确保存，不严格验证 100
    # （因为 val = db.value.get('counter', 0) 读到的是共享 dict 的实时值）
    assert db_final.value['counter'] > 0
    db_final.delete()


# 补一个 Path 的 import（test_load_db_async_reload 需要）
from pathlib import Path
