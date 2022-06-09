import socket


class ConnectionEventArgs:
    def __init__(self, host: str, connection: socket.socket):
        self.host = host
        self.connection = connection


class MessageEventArgs(ConnectionEventArgs):
    '''
    a new message distribution
    '''

    def __init__(self, host: str, connection: socket.socket, data: bytes):
        self.data = data
        super().__init__(
            host=host,
            connection=connection
        )


class NewConnectionEventArgs(ConnectionEventArgs):
    pass


class CloseConnectionEventArgs(ConnectionEventArgs):
    pass
