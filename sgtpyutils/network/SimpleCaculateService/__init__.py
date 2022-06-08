import json
from ..SimpleTcpService import SimpleTcpService, MessageEventArgs
from ...extensions import clazz


class SimpleCaculateService(SimpleTcpService):
    def handle_caculate(self, event: MessageEventArgs):
        data = event.data
        results = {}
        result = {}
        try:
            data = data.decode()
            first_line = data.find('\n')
            # have at least 2 lines
            if first_line > -1 and data.find('\n', first_line+1) > -1:
                exec(data, results)
                keys = [x for x in results if not x.startswith('_')]
                for x in keys:
                    result[x] = results[x]
                result = json.dumps(result)
            else:
                result = eval(data)
        except Exception as e:
            result = f'Error: {e}'
        event.connection.send(f'{result}\n'.encode())

    def __init__(self, host: str = '127.0.0.1'):
        return super().__init__(self.handle_caculate, host)
