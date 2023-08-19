from __future__ import annotations
import enum
from typing import overload
import datetime
import time
from .dateutil.parser import parser, parserinfo
_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


class DateFormat(enum.Enum):
    DEFAULT = '%Y-%m-%d %H:%M:%S'
    DEFAULT_MIL = '%Y-%m-%d %H:%M:%S'
    UTC = '%Y-%m-%dT%H:%M:%S%z'
    UTC_MIL = '%Y-%m-%dT%H:%M:%S.%f%z'


class DateTime(datetime.datetime):
    Format = DateFormat

    @overload
    def __new__(cls, date: datetime.datetime):
        ...

    @overload
    def __new__(cls, date: datetime.date):
        ...

    @overload
    def __new__(cls, date: str):
        ...

    @overload
    def __new__(cls, year: int, month: int, day: int, hour: int = ..., minute: int = ..., second: int = ..., microsecond: int = ..., tzinfo: datetime._TzInfo | None = ..., *, fold: int = ...):
        ...

    def __new__(cls, year: int = ..., month: int = ..., day: int = ..., hour: int = ..., minute: int = ..., second: int = ..., microsecond: int = ..., tzinfo: datetime._TzInfo | None = ..., *, fold: int = 0):
        if isinstance(year, str):
            x = DateTime.fromstring(year)
            return x
        if isinstance(year, datetime.datetime):
            x = year
            return DateTime(x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond, x.tzinfo, fold=x.fold)

        elif isinstance(year, datetime.date):
            x: datetime.date = year
            return DateTime(x.year, x.month, x.day, 0, 0, 0, 0, None, fold=0)

        if tzinfo is None:  # 无时区时，默认使用当前时区
            d = datetime.timedelta(seconds=-time.timezone)
            tzinfo = datetime.timezone(d)

        t = super().__new__(cls, year, month, day, hour, minute,
                            second, microsecond, tzinfo, fold=fold)
        return t

    @classmethod
    def fromstring(cls, date_str: str, dayfirst=False, yearfirst=False):
        r = parser(info=parserinfo(
            dayfirst=dayfirst,
            yearfirst=yearfirst,
        )).parse(date_str)

        return cls(r)

    def getTime(self) -> int:
        '''
        获取毫秒时间戳
        '''
        # 若未定义当前时区，则使用当前计算机时区
        delta = time.timezone if self.tzinfo is None else -self.utcoffset().total_seconds()

        # 将时间转换为UTC+0
        r = self.timestamp() - delta
        r *= 1e3  # 转换为毫秒
        return int(r)

    def tostring(self, format: str = DateFormat.DEFAULT) -> str:
        if isinstance(format, DateFormat):
            format = format.value
        return self.strftime(format)

    def date(self) -> DateTime:
        return DateTime(super().date())

    @classmethod
    def fromtimestamp(cls, t: int, tz=None):
        year_2300_second = 10000000000
        if t > year_2300_second:
            # 表示使用的毫秒制
            t /= 1e3

        # 将时间转换为UTC+0
        delta = time.timezone if tz is None else 0
        t += delta

        return super().fromtimestamp(t, tz)

    def toRelativeTime(self, target: DateTime = ..., show_full_date_if_over: int = 30) -> str:
        '''
        转换时间为相对时间
        @param target:DateTime:对比的时间，默认是现在
        @param show_full_date_if_over:int:当相差时间（天数）过多时返回绝对时间
        '''
        if target is Ellipsis:
            target = DateTime.now(tz=self.tzinfo)
        r = target - self
        delta_time = r.days + r.seconds / 86400
        if delta_time > show_full_date_if_over:
            return self.tostring()
        suffix = '前' if delta_time < 0 else '后'
        s_minute = 1 / 1440
        v_time = abs(delta_time)
        if v_time < s_minute:
            return '刚刚' if delta_time > 0 else '稍后'
        if v_time < 60 * s_minute:
            return f'{int(v_time*1440)}分钟{suffix}'
        if v_time < 2:
            return f'{int(v_time*24)}小时{suffix}'
        if v_time < 14:
            return f'{int(v_time)}天{suffix}'
        if v_time < 30:
            return f'{int(v_time/7)}周{suffix}'
        return f'{int(v_time)}天{suffix}'

    def __add__(self, other):
        t = datetime.timedelta
        if isinstance(other, int) or isinstance(other, float):
            other = t(milliseconds=other)
        return super().__add__(other)

    def __sub__(self, other):
        t = datetime.timedelta
        if isinstance(other, int) or isinstance(other, float):
            other = t(milliseconds=other)
        elif isinstance(other, str):
            other = DateTime.fromstring(other)

        if isinstance(other, t):
            return super().__sub__(other)
        if not isinstance(other, datetime.datetime):
            raise Exception(f'invalid type in date:{type(other)}')
        if not other.tzinfo is None and self.tzinfo is None:
            other = DateTime.fromtimestamp(other.timestamp())
            pass

        return super().__sub__(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            other = DateTime.fromtimestamp(other)
        elif isinstance(other, str):
            other = DateTime.fromstring(other)

        return super().__eq__(other)
