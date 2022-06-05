def padding_to(raw: bytes, padding: int, max_length: int = None):
    '''
    sometimes crypto need padding length to its requires
    '''
    c = len(raw)/padding
    block: int = int(c)
    if block != c:
        block += 1
    result = raw.rjust(padding*block, b'\0')
    if max_length:
        result = result[0:max_length]
    return result