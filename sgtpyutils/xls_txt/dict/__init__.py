from typing import Callable, Dict


def dict2sheet(data: Dict, formatter: Callable = None, header: dict = {'key': 'value', '-'*20: '-'*30}, margin: int = 30):
    '''
      convert key-value to sheet
      if formatter is set , no need to set margin
    '''
    result = dict(header)
    result.update(data)

    def left_just(x: str):
        return x.ljust(margin, ' ')
    if not formatter:
        def formatter(
            x, dic): return f'{left_just(x)}\t{hex(dic[x]) if isinstance(dic[x],int) else dic[x]}'
    output = [formatter(x, result) for x in result]
    return output
