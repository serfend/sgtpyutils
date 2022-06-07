import json
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


def start_client(s: SimpleCaculateService):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'start connect to local:{s.port}')
    client.connect(('127.0.0.1', s.port))
    return client


def test_caculator():
    s = test_service_start()
    client = start_client(s)

    rnd = random.Random()
    for i in range(10):
        a = rnd.randint(0, int(1e5))
        b = rnd.randint(0, int(1e5))
        client.send(f'{a}+{b}'.encode())
        data = client.recv(1024).decode().strip()
        data = int(data)
        c = a + b
        print(f'get result for {a} + {b} = {c} , recv {data}')
        assert c == data


def test_multi_lines():
    s = test_service_start()
    client = start_client(s)
    client.send(b'1+1\n')
    data = client.recv(1024)
    assert data == b'2\n', 'single line content should return direct'
    client.send(b'''
c = 1 + 1
    ''')
    data = client.recv(1024)
    result = data.decode().strip()
    result = json.loads(result)
    assert 'c' in result and result['c'] == 2


def test_exception():
    s = test_service_start()
    client = start_client(s)
    client.send(b'print(invalid\n')
    time.sleep(0.2)
    client.send(b'print(invalid\n')
    time.sleep(0.2)
    client.send(b'print(invalid\n')
    time.sleep(0.2)
    data = client.recv(1024)
    result = data.decode().strip()
    return test_caculator()