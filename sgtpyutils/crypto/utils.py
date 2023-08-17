from typing import Literal


def padding_to(raw: bytes, padding: int, max_length: int = None, padding_char: bytes = b'\0', align: Literal['left', 'right'] = 'right'):
    '''
    sometimes crypto need padding length to its requires
    '''
    c = len(raw)/padding
    block: int = int(c)
    if block != c:
        block += 1
    func = raw.rjust if align == 'right' else raw.ljust
    result = func(padding*block, padding_char)
    if max_length:
        result = result[0:max_length]
    return result
