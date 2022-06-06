import socket
import random
from sgtpyutils.network.SimpleCaculateService import SimpleCaculateService
s = SimpleCaculateService()
s.start()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', s.port))
rnd = random.Random()
while True:
    a = rnd.randint(0, int(1e3))
    b = rnd.randint(0, int(1e3))
    client.send(f'{a}+{b}'.encode())
    data = client.recv(1024).decode()
    c = a+b
    print(f'get result for {a} + {b} = {c} , recv {data}')
