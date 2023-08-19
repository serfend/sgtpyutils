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


def test_aop():
    @filebase_database.Database.require_database('test')
    def test(database: filebase_database.Database):
        assert database
        assert database.database_filename
    test()
