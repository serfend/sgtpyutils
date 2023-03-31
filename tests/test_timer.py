from sgtpyutils.timer import create_timer, Timer
import time


def test_timer_start():
    t = create_timer()
    assert not t.id is None


def test_time_counter():
    t = create_timer()
    time.sleep(1)
    assert t.spent > 0.5


def test_time_progrss():
    t = create_timer()
    t.progress_total = 100
    time.sleep(1)
    t.progress_current = 50
    assert t.progress_last == 0
    assert t.left_time > 0.8 and t.left_time < 2

    time.sleep(0.1)
    t.progress_current = 100
    assert t.progress_last == 50
    assert t.left_time < 0.1
    assert t.progress_description in t.progress_description_with_value
    assert t.progress_description == '100.00%'
