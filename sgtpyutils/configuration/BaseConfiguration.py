from __future__ import annotations
from sgtpyutils.logger import logger
CONFIG_Dict: dict[str, BaseConfiguration] = {}


class BaseConfiguration:
    def __init__(self, key: str) -> None:
        if CONFIG_Dict.get(key):
            logger.warning(f'duplicated config:{key}')
        CONFIG_Dict[key] = self

        self._cache: dict[str, bytes] = {}

    def get(self, key: str) -> bytes:
        return self._cache.get(key)

    def set(self, key: str, value: bytes):
        self._cache[key] = value
