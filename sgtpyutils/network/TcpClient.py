import random
from typing import Tuple
from ..logger import logger
import socket


def start_client(port: int, host: str = '127.0.0.1') -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'start connect to local:{port}')
    client.connect((host, port))
    return client


def generate_free(host: str, port: int = None, timeout: int = 15, min_port: int = 1001, max_port: int = 60000) -> Tuple:
    '''
    get a free port if port not specify
    if port is occupied and port is specified , a exception would be raise
    if port is occupied and port is NOT specified , new try for random port would be used
    return Tuple[socket.socket, int]
    '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(timeout)
    r = random.Random()
    if not port:
        s_port = r.randint(min_port, max_port)
    else:
        s_port = port
    max_try_time = 1e3
    while max_try_time > 0:
        try:
            server.bind((host, s_port))
            break
        except Exception as e:
            if port:
                raise e
            s_port += 1
            if s_port >= int(max_port):
                s_port = min_port
            max_try_time -= 1

    return (server, s_port)
