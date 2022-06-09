from typing import Callable, List


def list2sheet(lines: List, line_renderer: Callable = None, show_line_number: bool = True, max_show_count: int = 12, min_hide_count: int = 5, description: str = '     ...other {count} lines...'):
    '''
    show list in text mode
    '''
    result = [str(x) for x in lines if x]  # filter none
    result = [x for x in lines if len(x) > 0]  # filter empty
    count = len(result)
    skip_convert = None
    if count > max_show_count + min_hide_count:
        skip_convert = count - max_show_count
        half = int(max_show_count/2)
        result = result[0:half] + [None] + result[-half:]
    else:
        result = result

    def renderer(x: int):
        v = result[x]
        if not v:
            return str
        if line_renderer:
            v = line_renderer(v)
        if show_line_number:
            if skip_convert:
                line = f'{x if x<half else x-1:4d}: '
            else:
                line = f'{x:4d}: '
        else:
            line = ''
        content = f"{v if v else None}"
        return f'{line}{content}'

    result = [renderer(x) for x in range(len(result))]
    if skip_convert:
        result[half] = description.replace('{count}', str(skip_convert))
    return result
