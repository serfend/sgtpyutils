import threading
from typing import *
import socket
from ..EventArgs import *
from ....logger import logger
from ..BaseTcpHandler import BaseTcpHandler

class MessageHanlder(threading.Thread):
    def __init__(self,
                 connection: socket.socket,
                 remote_host: str,
                 callback: BaseTcpHandler,
                 daemon: bool = False) -> None:
        self.running = False

        self.connection = connection
        self.remote_host = remote_host
        self.callback = callback
        return super().__init__(daemon=daemon)

    def run(self) -> None:
        self.running = True
        super().run()
        self.__handle_message()
        self.running = False

    def __handle_message(self) -> None:
        connection = self.connection
        remote_host = self.remote_host
        while self.running:
            data = connection.recv(1024)
            if not data:
                break
            self.callback.OnMessage(
                connection=connection,
                remote_host=remote_host,
                data=data
            )
        try:
            connection.close()
        except:
            pass
        self.callback.OnCloseConnection()
        try:
            logger.debug(f'TCPService:: connection closed from {remote_host}')
        except:
            pass
