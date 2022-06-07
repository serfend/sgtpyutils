import socket
import random
import time
from sgtpyutils.logger import logger
from sgtpyutils.network.SimpleCaculateService import SimpleCaculateService


def test_service_start():
    s = SimpleCaculateService()
    s.start()
    assert s.is_listening == True
    return s


def test_caculator():
    s = test_service_start()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'start connect to local:{s.port}')
    client.connect(('127.0.0.1', s.port))
    rnd = random.Random()
    for i in range(10):
        a = rnd.randint(0, int(1e5))
        b = rnd.randint(0, int(1e5))
        client.send(f'{a}+{b}'.encode())
        data = client.recv(1024).decode()
        data = int(data)
        c = a + b
        print(f'get result for {a} + {b} = {c} , recv {data}')
        assert c == data
