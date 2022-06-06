import time
import random
import socket
import threading
from typing import Callable
from ...logger import logger


class SimpleTcpService(threading.Thread):
    def generate_free(self, port: int = None):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(15)
        host = self.host
        max_port = int(6e4)
        min_port = int(1001)
        if not port:
            s_port = random.Random().randint(min_port, max_port)
        while True:
            '''
            get a free port
            '''
            try:
                server.bind((host, s_port))
                break
            except Exception as e:
                s_port += 1
                if s_port >= int(max_port):
                    s_port = min_port
                time.sleep(0.5)

        self.socket = server
        return s_port

    def run(self) -> None:
        logger.debug(f'server start listening on {self.host}:{self.port}')
        self.socket.listen(1)
        self.server, self.remote_host = self.socket.accept()
        logger.debug(f'connection establish from {self.remote_host}')
        super().run()
        while self.running:
            data = self.server.recv(1024)
            if not data:
                logger.debug(f'connection closed from {self.remote_host}')
                return
            if self.on_message:
                self.on_message(data)

    def __init__(self, on_message: Callable, host: str = '127.0.0.1', port: int = None):
        self.on_message: Callable = on_message
        self.socket: socket.socket = None
        self.server: socket.socket
        self.host = host
        self.running = False
        self.port = self.generate_free(port)
        super().__init__()

    def start(self) -> None:
        self.running = True
        return super().start()
