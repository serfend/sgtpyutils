from typing import Callable, Dict


def dict2sheet(data: Dict, formatter: Callable = None, header: dict = {'key': 'value', '-'*20: '-'*30}, margin: int = 30):
    '''
      convert key-value to sheet
      formatter: Callable[line:str,lines_dict:Dict] -> str : specify how to format a line
            default set is lambda x,dic:f'{left_just(x)}\t{hex(dic[x]) if isinstance(dic[x],int) else dic[x]}'
            if formatter is set , no need to set margin
      
    '''
    result = dict(header)
    result.update(data)

    def left_just(x: str):
        x = str(x)
        return x.ljust(margin, ' ')
    if not formatter:
        def formatter(
            x, dic): return f'{left_just(x)}\t{hex(dic[x]) if isinstance(dic[x],int) else dic[x]}'
    output = [formatter(x, result) for x in result]
    return output
