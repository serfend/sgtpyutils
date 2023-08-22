from sgtpyutils.datetime import *

import time


def test_default_datetime():
    x = DateTime()
    assert x.tostring() == DateTime.now().tostring()
    delta1 = x.getTime()

    d = timedelta(seconds=100)
    tz = timezone(d)

    x.replace(tzinfo=tz)
    delta2 = x.getTime()

    assert delta1 == delta2, 'getTime应将时间统一'

    assert DateTime.today() == DateTime().date()


def test_default_delta():
    x = DateTime()
    delta = x.getDelta()
    assert time.timezone == delta


def test_date():
    date_mil_string = '2023-01-16 16:11:17.355789'
    date_string = '2023-01-16 16:11:17'
    x = DateTime.fromstring(date_mil_string)
    assert x.toRelativeTime() == date_string
    assert x.tostring() == date_string

    x = DateTime(date_mil_string)
    assert x.tostring() == date_string

    x2 = DateTime.fromstring('2023-01-06 15:16:11.355789')
    assert x.toRelativeTime(x2) == '10天前'

    x2 = DateTime.fromstring('2023-02-01 15:16:11.355789')
    assert x.toRelativeTime(x2) == '2周后'

    x2 = DateTime.fromstring('2023-01-16 15:16:11.355789')
    assert x.toRelativeTime(x2) == '55分钟前'

    t = x.getTime()
    assert 1673885477355 == t

    assert DateTime.fromtimestamp(t / 1e3).tostring() == date_string
    assert DateTime.fromtimestamp(t).tostring() == date_string

    yesterday = x - 86400e3
    assert yesterday == '2023-01-15 16:11:17.355789'

    assert yesterday.date() == '2023-01-15'


def test_offset_date():
    delta = timedelta(seconds=-time_timezone)
    tz = timezone(delta)
    x1 = DateTime(f'2023-08-19T15:00:00{tz}')
    x2 = DateTime('2023-08-19 15:00:00')
    assert (x2 - x1).total_seconds() == 0


def test_utc_format():
    t_mil = DateFormat.T_MIL
    t = DateFormat.T
    x1 = DateTime('2023-08-19T15:12:34.123+07:00')
    assert x1.tostring(t_mil) == '2023-08-19T15:12:34.123000'
    assert x1.tostring(t) == '2023-08-19T15:12:34'

    x1 = DateTime('2023-08-19 15:12:34.123')
    assert x1.tostring(t_mil) == '2023-08-19T15:12:34.123000'
    assert x1.tostring(t) == '2023-08-19T15:12:34'
