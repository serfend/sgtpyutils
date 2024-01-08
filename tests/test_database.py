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

    db.delete()