from ..SimpleTcpService import SimpleTcpService


class SimpleCaculateService(SimpleTcpService):
    def handle_caculate(self, data: bytes):
        try:
            result = eval(data.decode())
        except Exception as e:
            result = f'Error: {e}'
        self.server.send(f'{result}\n'.encode())

    def __init__(self, host: str = '127.0.0.1'):
        return super().__init__(self.handle_caculate, host)
