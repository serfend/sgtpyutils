from typing import List


def cast2bytes(input: any, encoding: str = 'utf-8') -> bytes:
    if isinstance(input, List):
        return b''.join([cast2bytes(x, encoding) for x in input])
    if isinstance(input, str):
        return input.encode(encoding)
    if isinstance(input, int):
        data = hex(input)[2:]
        if len(data) % 2:
            data = f'0{data}'
        return bytes.fromhex(data)
    return bytes(input)
