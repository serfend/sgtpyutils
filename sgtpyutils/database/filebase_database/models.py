"""数据模型：DateEncoder / DatabaseData"""

import json
import traceback
from typing import Any, Callable, Optional

from sgtpyutils.datetime import DateTime
from sgtpyutils.logger import logger


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DateTime):
            return obj.tostring()
        return super().default(obj)


class DatabaseData:
    """包装数据库中的数据，支持自定义序列化/反序列化。"""

    def __init__(
        self,
        data: Any,
        serializer: Optional[Callable],
        deserializer: Optional[Callable],
        name: str = '',
    ):
        self.data = data
        self.serializer = serializer
        self.deserializer = deserializer
        self.name = name

    def to_dict(self) -> Any:
        if self.serializer:
            try:
                return self.serializer(self.data)
            except Exception as ex:
                logger.error(
                    f'[{self.name}] fail to serializer {self.data}, '
                    f'ex:{ex}\n{traceback.format_exc()}'
                )
        return self.data if self.data is not None else {}

    def from_dict(self, data: Any):
        if self.deserializer:
            try:
                self.data = self.deserializer(data)
                return
            except Exception as ex:
                logger.error(
                    f'[{self.name}] fail to deserializer {data}, '
                    f'ex:{ex}\n{traceback.format_exc()}'
                )
        self.data = data if data is not None else {}
