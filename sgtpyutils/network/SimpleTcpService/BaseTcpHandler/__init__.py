import threading
from typing import *
from ..EventArgs import *


class BaseTcpHandler(threading.Thread):
    def __init__(
        self,
        on_message: Callable[[MessageEventArgs], None],
        on_new_connection: Callable[[NewConnectionEventArgs], None] = None,
        on_close_connection: Callable[[CloseConnectionEventArgs], None] = None,
        daemon: bool | None = ...
    ):
        self.on_message = on_message
        self.on_new_connection = on_new_connection
        self.on_close_connection = on_close_connection
        return super().__init__(daemon=daemon)

    def OnMessage(self, remote_host: str, connection: socket.socket, data: bytes):
        if self.on_message:
            e = MessageEventArgs(
                host=remote_host,
                connection=connection,
                data=data
            )
            self.on_message(e)

    def OnNewConnection(self, remote_host: str, connection: socket.socket):
        if self.on_new_connection:
            e = NewConnectionEventArgs(remote_host, connection)
            return self.on_new_connection(e)

    def OnCloseConnection(self):
        pass
