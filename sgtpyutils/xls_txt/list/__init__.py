from typing import Callable, List


def list2sheet(lines: List, line_renderer: Callable = None, show_line_number: bool = True, max_show_count: int = 5, min_hide_count: int = 5, description: str = '     ...other {count} lines...'):
    '''
    show list in text mode
    '''
    count = len(lines)
    skip_convert = None
    if count > max_show_count + min_hide_count:
        skip_convert = count - max_show_count
        half = int(max_show_count/2)
        result = lines[0:half] + [None] + lines[-half:]
    else:
        result = lines
    if skip_convert:
        result[half] = description.replace('{count}', str(skip_convert))

    def renderer(x: int):
        v = result[x]
        if line_renderer:
            v = line_renderer(v)
        if show_line_number:
            line = f'{x if x<half else x-1:4d}: '
        else:
            line = ''
        content = f"{v if v else None}"
        return f'{line}{content}'

    result = [renderer(x) for x in range(len(result))]
    return result
