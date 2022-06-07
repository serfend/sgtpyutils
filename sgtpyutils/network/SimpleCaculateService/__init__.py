import json
from ..SimpleTcpService import SimpleTcpService
from ...extensions import clazz


class SimpleCaculateService(SimpleTcpService):
    def handle_caculate(self, data: bytes):
        results = {}
        result = {}
        try:
            data = data.decode()
            if data.find('\n') > -1:
                exec(data, results)
                keys = [x for x in results if not x.startswith('_')]
                for x in keys:
                    result[x] = results[x]
                result = json.dumps(result)
            else:
                result = eval(data)
        except Exception as e:
            result = f'Error: {e}'
        self.server.send(f'{result}\n'.encode())

    def __init__(self, host: str = '127.0.0.1'):
        return super().__init__(self.handle_caculate, host)
