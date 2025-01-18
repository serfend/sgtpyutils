import pathlib2
import logging
import logging.handlers

class CommonLog(logging.Logger):
    @classmethod
    def create(
        cls,
        level=logging.INFO,
        log_dir='log/common.log',
        fmt: str = '%(asctime)s:%(message)s',
        maxBytes=1024 * 1024,
        backupCount=5,
    ):
        self = logging.getLogger(log_dir)
        self.setLevel(level)  # 设置日志级别
        path = pathlib2.Path(log_dir)
        if path.parent.parts and not path.parent.exists():
            path.parent.mkdir(parents=True)
        file_handler = logging.handlers.RotatingFileHandler(path.as_posix(), maxBytes=maxBytes, backupCount=backupCount)
        formatter = logging.Formatter(fmt)  # 实例化formatter。
        stream_handler = logging.StreamHandler()  # 往屏幕上输出
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.addHandler(stream_handler)
        self.addHandler(file_handler)
        return self


class CommpnLog(CommonLog):
    pass