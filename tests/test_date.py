from sgtpyutils.datetime import DateTime


def test_date():
    date_mil_string = '2023-01-16 16:11:17.355789'
    date_string = '2023-01-16 16:11:17'
    x = DateTime.fromstring(date_mil_string)
    assert x.toRelativeTime() == date_string
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
