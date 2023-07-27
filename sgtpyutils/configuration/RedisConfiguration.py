import redis
from .BaseConfiguration import *


class RedisConfiguration(BaseConfiguration):
    def __init__(self, key: str, **kwargs) -> None:
        self.client = redis.StrictRedis(**kwargs)
        super().__init__(key)

    def set(self, key: str, value: bytes):
        return self.client.set(key, value)

    def get(self, key: str):
        return self.client.get(key)
