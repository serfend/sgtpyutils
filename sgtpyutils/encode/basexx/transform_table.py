import base64
from . import base58
from . import base91
basexx = {}
basexx['b16decode'] = base64.b16decode
basexx['b32decode'] = base64.b32decode
basexx['b64decode'] = base64.b64decode
basexx['b85decode'] = base64.b85decode
basexx['b32decode'] = base64.b32decode
basexx['b58decode'] = base58.b58decode
basexx['b91decode'] = base91.b91decode

basexx['b16encode'] = base64.b16encode
basexx['b32encode'] = base64.b32encode
basexx['b64encode'] = base64.b64encode
basexx['b85encode'] = base64.b85encode
basexx['b32encode'] = base64.b32encode
basexx['b58encode'] = base58.b58encode
basexx['b91encode'] = base91.b91encode


def switch_base_table_encode(algo_name: str, default_table: str, problem_table: str, content: any):
    if isinstance(content, str):
        print('encode excepted content to be a bytes , assume utf-8 encode.')
        content = content.encode('utf-8')
    if isinstance(problem_table, bytes):
        print('encode excepted problem_table to be a str , assume ascii encode.')
        problem_table = problem_table.decode('ascii')

    if problem_table is None:
        problem_table = default_table
    if len(problem_table) < len(default_table):
        problem_table = str.ljust(
            problem_table, len(default_table), '?')
        print(f'length not enough,padding:\n{problem_table}')

    char_map = str.maketrans(default_table, problem_table)
    if not algo_name in basexx:
        raise Exception(f'no such algorithm {algo_name}')
    f = basexx[algo_name]
    encode_content = f(content)
    if isinstance(encode_content, bytes):
        encode_content = encode_content.decode('ascii')
    result = encode_content.translate(char_map)
    return result


def switch_base_table_decode(algo_name: str, default_table: str, problem_table: str, content: any):
    if isinstance(content, bytes):
        print('decode excepted content to be a str , assume ascii encode.')
        content = content.decode('ascii')
    if isinstance(problem_table, bytes):
        print('decode excepted problem_table to be a str , assume ascii encode.')
        problem_table = problem_table.decode('ascii')
    if problem_table is None:
        problem_table = default_table
    if len(problem_table) < len(default_table):
        problem_table = str.ljust(
            problem_table, len(default_table), '?')
        print(f'length not enough,padding:\n{problem_table}')
    char_map = str.maketrans(problem_table, default_table)
    trans = content.translate(char_map)
    if not algo_name in basexx:
        raise Exception(f'no such algorithm {algo_name}')
    f = basexx[algo_name]
    result = f(trans)
    return result
