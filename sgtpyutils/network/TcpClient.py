from ..logger import logger
import socket


def start_client(port: int, host: str = '127.0.0.1') -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'start connect to local:{port}')
    client.connect((host, port))
    return client
