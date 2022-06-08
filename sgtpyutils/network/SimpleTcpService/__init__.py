from concurrent.futures import ThreadPoolExecutor
import time
import random
import socket
import threading
from typing import Callable
from ...logger import logger


class ConnectionEventArgs:
    def __init__(self, host: str, connection: socket):
        self.host = host
        self.connection = connection


class MessageEventArgs(ConnectionEventArgs):
    '''
    a new message distribution
    '''

    def __init__(self, host: str, connection: socket, data: bytes):
        self.data = data
        super().__init__(
            host=host,
            connection=connection
        )


class NewConnectionEventArgs(ConnectionEventArgs):
    pass


class SimpleTcpService(threading.Thread):
    def generate_free(self, port: int = None):
        '''
        get a free port if port not specify
        if port is occupied and port is specified , a exception would be raise
        if port is occupied and port is NOT specified , new try for random port would be used
        '''
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

    def handle_message(self, connection: socket, remote_host: str) -> None:
        while self.running:
            data = connection.recv(1024)
            if not data:
                break
            if self.on_message:
                e = MessageEventArgs(
                    host=remote_host,
                    connection=connection,
                    data=data
                )
                self.on_message(e)
        try:
            connection.close()
        except:
            pass
        logger.debug(f'TCPService:: connection closed from {remote_host}')

    def handle_new_connection(self, connection: socket, remote_host: str) -> None:
        logger.debug(
            f'TCPService:: connection establish from {remote_host}')
        if self.on_new_connection:
            e = NewConnectionEventArgs(
                host=remote_host,
                connection=connection
            )
            self.on_new_connection(e)
        self.ThreadPoolExecutor.submit(self.handle_message,
                                       connection=connection,
                                       remote_host=remote_host,
                                       )

    def run(self) -> None:
        super().run()
        logger.debug(
            f'TCPService:: server start listening on {self.host}:{self.port}')
        self.__on_listen(True)
        self.socket.listen(1)
        while self.is_listening and self.running:
            try:
                connection, remote_host = self.socket.accept()
                self.handle_new_connection(connection, remote_host)
            except TimeoutError as e:
                pass
            except Exception as e:
                logger.info(f'TCPService:: listing stop for exception:{e}')
        self.__on_listen(False)

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

    def __init__(self, on_message: Callable, on_new_connection: Callable = None, host: str = '127.0.0.1', port: int = None, ensure_start: bool = True):
        self.is_listening = False  # whether self-listening
        self.on_message: Callable = on_message
        self.on_new_connection: Callable = on_new_connection
        
        self.on_listen_start: Callable = None
        self.on_listen_end: Callable = None
        self.socket: socket.socket = None
        self.host = host
        self.running = False
        self.port = self.generate_free(port)
        self.ThreadPoolExecutor = ThreadPoolExecutor()
        super().__init__()
        self.daemon = True  # as daemon thread default
        if ensure_start:
            self.ensure_start()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        return super().start()
