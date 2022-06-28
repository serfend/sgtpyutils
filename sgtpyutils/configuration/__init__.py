
from ..logger import logger
import json
import os
from typing import Dict
configuration_path: str = '.sgt.conf'
config: Dict = None


def get_config_path() -> str:
    global configuration_path
    path = os.path.join(os.path.expanduser('~'), configuration_path)
    return path


def load(config_path: str = None, reload: bool = False) -> Dict:
    if not config_path is None:
        global configuration_path
        if config_path != configuration_path:
            reload = True
        configuration_path = config_path
    global config
    if config is None:
        reload = True
    if not reload:
        return config
    p = get_config_path()
    if not os.path.exists(p):
        save(reload=False)
    with open(p, 'r', encoding='utf-8') as f:
        config_content = f.read()
    config = json.loads(config_content) or {}
    return config


def save(new_config: Dict = None, reload: bool = False):
    global config
    data = json.dumps(config if new_config is None else new_config)
    with open(get_config_path(), 'w', encoding='utf-8') as f:
        f.write(data)
    if reload:
        load()


def get(key: str = None, default: any = None) -> any:
    data = load()
    if not key in data:
        return default
    return data[key]


def set(key: str, value: any = None):
    load()
    global config
    key = str(key)
    if not key:
        raise Exception('key must be set')
    config[key] = value
