import socket
import random
from sgtpyutils.network.SimpleCaculateService import SimpleCaculateService


def test_caculator():
    s = SimpleCaculateService()
    s.setDaemon(True)
    s.start()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    
