from __future__ import annotations
import json
import redis
from functools import wraps
import threading
from sgtpyutils.logger import logger
from sgtpyutils.functools import AssignableArg
import time


class RedisCallbackEvent:
    data: str = None
    channel: str = None

    def __init__(self, channel: str, data: str) -> None:
        self.channel = channel
        self.data = data

    def __str__(self) -> str:
        return f'[{self.channel}]{self.data}'


Subscribers: dict[str, list[function]] = {}


class SubscriberWorker(threading.Thread):
    pb: redis.client.PubSub = None
    client: redis.client.Redis = None

    DEFAULT_Config = {
        'host': '127.0.0.1',
        'port': 38379,
        'db': 7,
        'password': 'defaultredispsw@ts.8.8'
    }

    @staticmethod
    def get_client():
        if SubscriberWorker.client is None:
            config = SubscriberWorker.DEFAULT_Config
            SubscriberWorker.client = redis.client.Redis(**config)

        return SubscriberWorker.client

    @staticmethod
    def get_pubsub():
        if SubscriberWorker.pb is None:
            SubscriberWorker.pb = SubscriberWorker.get_client().pubsub()
        return SubscriberWorker.pb

    def __init__(self) -> None:
        super().__init__(name=__class__.__name__,  daemon=True)

    def handle_msg(self, channel: str, value: str):
        callbacks = Subscribers.get(channel)
        if not callbacks:
            logger.debug(f'redis_subscribe[{channel}]:{value}')
            return
        for callback in callbacks:
            arg = AssignableArg(method=callback)
            data = RedisCallbackEvent(channel, value)
            arg.assign_by_type(RedisCallbackEvent, data)
            try:
                callback(*arg.args, **arg.kwargs)
            except Exception as ex:
                msg = 'fail run redis_callback:'
                logger.warning(f'{msg}{callback.__name__},{ex}')

    def run_once(self):
        pb = SubscriberWorker.get_pubsub()
        for x in pb.listen():
            _type = x.get('type')
            if _type == 'subscribe':
                logger.debug(f'new subscribe:{x}')
                continue
            channel = x.get('channel')
            if isinstance(channel, bytes):
                channel = channel.decode()

            data = x.get('data')
            if isinstance(data, bytes):
                data = data.decode()

            self.handle_msg(channel, data)
        logger.debug('redis_subscribe handler run_once completed')

    def run(self) -> None:
        while True:
            self.run_once()
            time.sleep(0.1)

        return super().run()


_redis_callbacker = SubscriberWorker()
_redis_callbacker.start()


class RedisSubscriber:

    @staticmethod
    def publish(event: RedisCallbackEvent):
        channel = event.channel  # 'sec:device:status:update'
        data = event.data
        if isinstance(data, dict):
            data = json.dumps(data)
        if not isinstance(data, str):
            data = str(data)
        logger.debug(f'send message at [{channel}]{data}')
        return SubscriberWorker.get_client().publish(channel, data)

    @staticmethod
    def redis_subscribe_callback(channel: str):
        '''
        当有推送时调用
        method的RedisCallbackData参数将被填充并尝试调用
        '''
        # 如无此句，将导致因闭包channel变量覆盖
        # 从而只有最后一个注册的事件能够被回调
        logger.debug(f'start redis_subscribe hook:{channel}')

        def wrap(method: function):
            return RedisSubscriber.redis_subscribe(channel, method)
        return wrap

    @staticmethod
    def redis_subscribe(channel: str, callback_method: function):
        if not Subscribers.get(channel):
            Subscribers[channel] = []
            SubscriberWorker.get_pubsub().subscribe(channel)

        Subscribers[channel].append(callback_method)

        @wraps(callback_method)
        def wrapper(*args, **kwargs):
            return callback_method(*args, **kwargs)
        return wrapper

    @staticmethod
    def require_redis():
        def require_func(method: function):
            @wraps(method)
            def wrapper(*args, **kwargs):
                x_args = AssignableArg(args, kwargs, method)
                client = SubscriberWorker.get_client()
                x_args.assign_by_type(redis.client.Redis, client)
                result = method(*x_args.args, **x_args.kwargs)
                return result
            return wrapper
        return require_func
