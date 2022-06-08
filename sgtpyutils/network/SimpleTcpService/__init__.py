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
        else:
            s_port = port
        max_try_time = 1e3
        while max_try_time > 0:
            '''
            get a free port
            '''
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

        self.socket = server
        return s_port

    def run(self) -> None:
        logger.debug(f'server start listening on {self.host}:{self.port}')
        self.__on_listen(True)
        self.socket.listen(1)
        self.server, self.remote_host = self.socket.accept()
        self.__on_listen(False)
        logger.debug(f'connection establish from {self.remote_host}')
        super().run()
        while self.running:
            data = self.server.recv(1024)
            if not data:
                logger.debug(f'connection closed from {self.remote_host}')
                return
            if self.on_message:
                self.on_message(data)

    def ensure_start(self):
        if self.is_listening:
            return
        if not self.running:
            self.start()
        counter = 100
        while not self.is_listening and counter:
            time.sleep(0.1)
            counter -= 1

    def __on_listen(self, is_start: bool):
        self.is_listening = is_start
        if is_start and self.on_listen_start:
            self.on_listen_start()
        elif not is_start and self.on_listen_end:
            self.on_listen_end()

    def __init__(self, on_message: Callable, host: str = '127.0.0.1', port: int = None, ensure_start: bool = True):
        self.is_listening = False  # whether self-listening
        self.on_message: Callable = on_message
        self.on_listen_start: Callable = None
        self.on_listen_end: Callable = None
        self.socket: socket.socket = None
        self.server: socket.socket
        self.host = host
        self.running = False
        self.port = self.generate_free(port)
        super().__init__()
        self.daemon = True  # as daemon thread default
        if ensure_start:
            self.ensure_start()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        return super().start()
