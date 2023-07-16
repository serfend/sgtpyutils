from sgtpyutils.logger import logger
from sgtpyutils.ascii import printable
from sgtpyutils.extensions.itertools import run_cycle
from enum import Enum
import hashlib

ALG_CLASS_ANY = 0
ALG_CLASS_SIGNATURE = 8192
ALG_CLASS_MSG_ENCRYPT = 16384
ALG_CLASS_DATA_ENCRYPT = 24576
ALG_CLASS_HASH = 32768
ALG_CLASS_KEY_EXCHANGE = 40960
ALG_CLASS_ALL = 57344  # / * (7 << 13) * /
ALG_TYPE_ANY = 0
ALG_TYPE_DSS = 512
ALG_TYPE_RSA = 1024
ALG_TYPE_BLOCK = 1536
ALG_TYPE_STREAM = 2048
ALG_TYPE_DH = 2560  # / * (5 << 9) * /
ALG_TYPE_SECURECHANNEL = 3072  # / * (6 << 9) * /
ALG_SID_ANY = 0
ALG_SID_RSA_ANY = 0
ALG_SID_RSA_PKCS = 1
ALG_SID_RSA_MSATWORK = 2
ALG_SID_RSA_ENTRUST = 3
ALG_SID_RSA_PGP = 4
ALG_SID_DSS_ANY = 0
ALG_SID_DSS_PKCS = 1
ALG_SID_DSS_DMS = 2
ALG_SID_DES = 1
ALG_SID_3DES = 3
ALG_SID_DESX = 4
ALG_SID_IDEA = 5
ALG_SID_CAST = 6
ALG_SID_SAFERSK64 = 7
ALG_SID_SAFERSK128 = 8
ALG_SID_3DES_112 = 9
ALG_SID_SKIPJACK = 10
ALG_SID_TEK = 11
ALG_SID_CYLINK_MEK = 12
ALG_SID_RC5 = 13
ALG_SID_RC2 = 2
ALG_SID_RC4 = 1
ALG_SID_SEAL = 2
ALG_SID_MD2 = 1
ALG_SID_MD4 = 2
ALG_SID_MD5 = 3
ALG_SID_SHA = 4
ALG_SID_MAC = 5
ALG_SID_RIPEMD = 6
ALG_SID_RIPEMD160 = 7
ALG_SID_SSL3SHAMD5 = 8
ALG_SID_HMAC = 9
ALG_SID_TLS1PRF = 10
ALG_SID_AES_128 = 14
ALG_SID_AES_192 = 15
ALG_SID_AES_256 = 16
ALG_SID_AES = 17
ALG_SID_EXAMPLE = 80

CALG_MD2 = (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD2)
CALG_MD4 = (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD4)
CALG_MD5 = (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD5)
CALG_SHA = (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_SHA)
CALG_SHA1 = CALG_SHA
CALG_MAC = (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MAC)
CALG_3DES = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | 3)
CALG_CYLINK_MEK = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | 12)
CALG_SKIPJACK = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | 10)
CALG_KEA_KEYX = (ALG_CLASS_KEY_EXCHANGE | ALG_TYPE_STREAM | ALG_TYPE_DSS | 4)
CALG_RSA_SIGN = (ALG_CLASS_SIGNATURE | ALG_TYPE_RSA | ALG_SID_RSA_ANY)
CALG_DSS_SIGN = (ALG_CLASS_SIGNATURE | ALG_TYPE_DSS | ALG_SID_DSS_ANY)
CALG_RSA_KEYX = (ALG_CLASS_KEY_EXCHANGE | ALG_TYPE_RSA | ALG_SID_RSA_ANY)
CALG_DES = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_DES)
CALG_RC2 = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_RC2)
CALG_RC4 = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_STREAM | ALG_SID_RC4)
CALG_SEAL = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_STREAM | ALG_SID_SEAL)
CALG_DH_EPHEM = (ALG_CLASS_KEY_EXCHANGE | ALG_TYPE_STREAM |
                 ALG_TYPE_DSS | ALG_SID_DSS_DMS)
CALG_DESX = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_DESX)
CALG_AES_128 = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_AES_128)
CALG_AES_192 = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_AES_192)
CALG_AES_256 = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_AES_256)
CALG_AES = (ALG_CLASS_DATA_ENCRYPT | ALG_TYPE_BLOCK | ALG_SID_AES)


class HashAlgo(Enum):
    md5 = CALG_MD5
    sha1 = CALG_SHA1
    sha224 = 'sha224'
    sha256 = 'sha256'
    sha384 = 'sha384'
    sha512 = 'sha512'


def get_hash(content: bytes, hash_name: HashAlgo = HashAlgo.md5, key: bytes = None) -> str:
    '''
      get hexdigest of a content
      @content:bytes: str|bytes
      @hash_name: HashAlgo: named of hash
      @key:bytes: if use rc4 etc. , key should be added
    '''
    if isinstance(hash_name, HashAlgo):
        hash_name = hash_name.name
    assert hasattr(hashlib, hash_name), 'no such hash algorithm'
    f = getattr(hashlib, hash_name)
    model = f()
    if isinstance(content, str):
        content = content.encode('ascii')
    model.update(content)
    return model.hexdigest()


def brute_hash(target: str, hash_name: HashAlgo = HashAlgo.md5, table: str = None, brute_length: int = 8, interval_step=123456, key: bytes = None) -> str:
    '''
    to brute hash raw content
    @target:str:target-string after hash
    @hash_name:HashAlgo: named of hash
    @table:str: chars for enum.
    @brute_length:int: max length for attempt
    @interval_step: show log every x steps
    @key:bytes: if use rc4 etc. , key should be added
    @return:str:raw-content of such hash
    '''
    def func(raw: str) -> str:
        return get_hash(raw, hash_name, key)
    return brute_func(
        target=target,
        func=func,
        table=table,
        brute_length=brute_length,
        interval_step=interval_step
    )


def brute_func(target: str, func: callable, table: str = None, brute_length: int = 8, interval_step: int = 123456) -> str:
    '''
    to brute result from raw content
    @target:str:str:target-string after run
    @func:callble[str,str]:handler function
    @table:str: chars for enum.
    @brute_length:int: max length for attempt
    @interval_step:int: show log every x steps
    @return:str:raw-content of such function
    '''
    table = table or printable
    for index, i in run_cycle(table=table, length=brute_length):
        if index % interval_step == 0:
            logger.debug(f'running...:{i}')
        base = ''.join(i)
        target_string = f'{base}'
        if func(target_string) == target:
            logger.info(f'found result::{target_string}')
            return target_string
    return None
