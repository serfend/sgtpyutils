SCALE_Kilo: tuple[str, str] = ('KMGTPEZY', '33333333')
SCAKE_CN: tuple[str, str] = ('万亿兆京垓秭壤沟涧正载', '44444444444')
SCAKE_Coin: tuple[str, str] = ('铜银金砖', '0222')


def __number_sci_raw(raw: int, scales: tuple[str, str] = None) -> list[tuple[int, str]]:
    '''
    将数值转换为计数
    @param raw int:原始数值
    @param scales tuple[str,str]:转换规则
    @return list:结果
    '''
    if not scales:
        scales = SCALE_Kilo
    current_level = 0
    scale_str = scales[0]
    scale_rate = scales[1]
    scale_rate_max = len(scale_rate)
    result = []
    while True:
        if scale_rate_max <= current_level:
            break
        cur_rank = int(scale_rate[current_level])
        current_limit = pow(10, cur_rank)

        current_str = scale_str[current_level -
                                1] if current_level > 0 else ''  # 当前计量单位
        cur_result = (int(raw % current_limit), current_str)   # 当前数值
        result.append(cur_result)

        raw = int(raw / current_limit)  # 取下一层级数值
        if raw == 0:
            break
        current_level += 1

    result.reverse()
    return result


def number_sci_raw_value(raw: int, scales: tuple[str, str] = None, limit: int = 3) -> str:
    '''
    将数值转换为带小数点的计数
    '''
    r = __number_sci_raw(raw, scales)
    decimal = ''
    index = 1
    max_scale = len(r)
    if max_scale == 0:
        return '0'
    while len(decimal) < limit:
        if index >= max_scale:
            break
        decimal += f'{r[index][0]}'
        index += 1
    decimal = decimal[0:limit]
    result = f'{r[0][0]}.{decimal}{r[0][1]}'
    return result

def number_sci_raw_str(raw: int, scales: tuple[str, str] = None)->str:
    '''
    将数值转换为各个计量单位值
    '''
    r = __number_sci_raw(raw, scales)
    result = [f'{x[0]}{x[1]}' for x in r]
    return result


def number_sci(raw: int, scales: tuple = None) -> str:
    '''
    将数值转换为计数
    @param raw int:原始数值
    @param scales tuple[str,str]:转换规则
    @return str:结果
    '''
    result = number_sci_raw_str(raw, scales)
    return str.join('', result)
