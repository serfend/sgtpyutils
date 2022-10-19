import logging
import logging.handlers
import colorlog
logger: logging.Logger = None
file_handler: logging.Handler = None
console_handler: logging.Handler = None

logger.removeHandler()
LOG_FILE = 'log.log'


def set_log_file(filename: str):
    global LOG_FILE
    LOG_FILE = filename
    init()


def disable(file: bool = True, console: bool = True):
    if not logger:
        return
    if file:
        logger.removeHandler(file_handler)
    if console:
        logger.removeHandler(console_handler)


def redefine_level_name():
    from logging import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET
    dic = {
        CRITICAL: '!!',
        FATAL: '!!',
        ERROR: '-',
        WARNING: '!',
        WARN: '!',
        INFO: '+',
        DEBUG: '*',
        NOTSET: '~',
    }
    for i in dic:
        logging.addLevelName(i, dic[i])


redefine_level_name()


def init():
    global LOG_FILE
    logger = logging.getLogger('common')  # 获取名为commomn的logger。
    fmt = '%(asctime)s [%(levelname)s] %(message)s :%(filename)s:%(lineno)s-%(levelno)s  %(pathname)s on(%(module)s.%(funcName)s) at %(process)d@%(threadName)s  '  # 定义日志格式
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter(fmt)   # 实例化formatter。
    file_handler.setFormatter(formatter)      # 为handler添加formatter。
    logger.addHandler(file_handler)           # 为logger添加handler。

    fmt = '%(asctime)s [%(levelname)s] %(message)s'  # 定义日志格式
    colors = {
        '*': 'light_blue',
        '+': 'green',
        '!': 'yellow',
        '-': 'red',
        '!!': 'purple,bg_white',
    }
    fmt_colored = colorlog.ColoredFormatter(
        f'%(log_color)s{fmt}', datefmt=None, reset=True, log_colors=colors)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt_colored)      # 为handler添加formatter。
    logger.addHandler(console_handler)           # 为logger添加handler。

    logger.setLevel(logging.DEBUG)


init()
