from .transform_table import switch_base_table_encode, switch_base_table_decode

base91_default_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"'
base85_default_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
base64_default_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
base58_default_table = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
base36_default_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
base32_default_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
base16_default_table = '123456789ABCDEF'

def base91_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b91decode', base91_default_table, problem_table, content)


def base85_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b85decode', base85_default_table, problem_table, content)


def base64_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b64decode', base64_default_table, problem_table, content)


def base58_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b58decode', base58_default_table, problem_table, content)


def base36_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b36decode', base36_default_table, problem_table, content)


def base32_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b32decode', base32_default_table, problem_table, content)


def base16_decode(content: str, problem_table: str = None):
    return switch_base_table_decode('b16decode', base16_default_table, problem_table, content)


def base91_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b91encode', base91_default_table, problem_table, content)

def base85_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b85encode', base85_default_table, problem_table, content)


def base64_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b64encode', base64_default_table, problem_table, content)


def base58_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b58encode', base58_default_table, problem_table, content)


def base36_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b36encode', base36_default_table, problem_table, content)


def base32_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b32encode', base32_default_table, problem_table, content)


def base16_encode(content: str, problem_table: str = None):
    return switch_base_table_encode('b16encode', base16_default_table, problem_table, content)
