import os
import random
from sgtpyutils import configuration


def test_primary():
    r = random.randint(int(1e7), int(1e8)-1)
    configuration.configuration_path = f'.tmp.{r}.conf'
    configuration.save({
        'test': 1
    })
    p = configuration.get_config_path()
    assert os.path.exists(p)
    with open(p, 'r', encoding='utf-8') as f:
        data = f.read()
        assert data == '{"test": 1}'

    config = configuration.load()
    assert 'test' in config
    assert config['test'] == 1
    os.remove(p)


def test_set_get():
    r = random.randint(int(1e7), int(1e8)-1)
    configuration.load(config_path=f'.tmp.{r}.conf')
    configuration.set('test', 1)
    assert configuration.get('test', 1)
    configuration.set('test2', '1')
    assert configuration.get('test2', '1')
