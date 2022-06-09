import time
import socket
from typing import *
from ...logger import logger
from ..TcpClient import generate_free

from .EventArgs import NewConnectionEventArgs, MessageEventArgs,  CloseConnectionEventArgs
from .MessageHandler import MessageHanlder
from .BaseTcpHandler import BaseTcpHandler


class SimpleTcpService(BaseTcpHandler):

    def __handle_new_connection(self, connection: socket.socket, remote_host: str) -> None:
        logger.debug(
            f'TCPService:: connection establish from {remote_host}')
        if self.on_new_connection:
            accept = self.OnNewConnection(
                remote_host=remote_host, connection=connection)
            if not accept:
                return
        t = MessageHanlder(
            connection=connection,
            remote_host=remote_host,
            daemon=True,
            callback=self
        )
        self.threads.append(t)
        t.start()

    def run(self) -> None:
        super().run()
        logger.debug(
            f'TCPService:: server start listening on {self.host}:{self.port}')
        self.__on_listen(is_start=True)
        self.socket.listen(1)
        try:
            while self.is_listening and self.running:
                try:
                    connection, remote_host = self.socket.accept()
                except TimeoutError as e:
                    pass
                except Exception as e:
                    logger.info(f'TCPService:: listing stop for exception:{e}')
                self.__handle_new_connection(connection, remote_host)
        except:
            pass
        self.stop()
        self.__on_listen(is_start=False)

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
        try:
            if is_start and self.on_listen_start:
                self.on_listen_start()
            elif not is_start and self.on_listen_end:
                self.on_listen_end()
        except:
            pass

    def stop(self):
        for t in self.threads:
            t.join()

    def __init__(self,
                 on_message: Callable[[MessageEventArgs], None],
                 on_new_connection: Callable[[
                     NewConnectionEventArgs], None] = None,
                 on_close_connection: Callable[[
                     CloseConnectionEventArgs], None] = None,
                 host: str = '127.0.0.1', port: int = None, ensure_start: bool = True,
                 daemon: bool | None = ...):
        self.is_listening = False  # whether self-listening
        self.on_message: Callable = on_message
        self.on_new_connection: Callable = on_new_connection

        self.on_listen_start: Callable = None
        self.on_listen_end: Callable = None
        self.socket: socket.socket = None
        self.host = host
        self.running = False
        self.socket, self.port = generate_free(
            host=host,
            port=port,
        )
        super().__init__(
            on_message=on_message,
            on_new_connection=on_new_connection,
            on_close_connection=on_close_connection,
        )
        self.threads: List[MessageHanlder] = []
        self.daemon = True  # as daemon thread default
        if ensure_start:
            self.ensure_start()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        return super().start()
