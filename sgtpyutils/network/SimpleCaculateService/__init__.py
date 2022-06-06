from ..SimpleTcpService import SimpleTcpService


class SimpleCaculateService(SimpleTcpService):
    def handle_caculate(self, data: bytes):
        result = eval(data.decode())
        self.server.send(str(result).encode())

    def __init__(self, host: str = '127.0.0.1'):
        return super().__init__(self.handle_caculate, host)
