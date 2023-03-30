import time
import random
import math
timer_list = {}


def create_timer(id: str = None):
    if id is None:
        id = str(random.randint(int(1e7), int(1e8)-1))

    if id in timer_list:
        return timer_list[id]
    t = Timer()
    t.id = id
    timer_list[id] = t
    return t


class Timer:
    def __init__(self) -> None:
        self.progress_total = 0
        self.progress_current = 0
        self.start()

    def start(self) -> float:
        self.time_start = time.time()
        return self.time_start

    @property
    def spent(self) -> float:
        return time.time() - self.time_start

    @property
    def progress(self) -> float:
        if self.progress_total <= 0:
            return 0
        return self.progress_current / self.progress_total

    @property
    def progress_description(self) -> str:
        p = self.progress
        d = math.ceil(p * 10000) / 100
        return f'{d}%'

    @property
    def left_time(self) -> float:
        '''
        返回剩余时间/秒
        '''
        p = self.progress
        if p <= 0:
            return 0
        spent = self.spent
        return spent / p - spent
