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

print('CALG_MD5', hex(CALG_MD5))
print('CALG_SHA1', hex(CALG_SHA1))


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

      Arguments:
        content:bytes: str|bytes
        hash_name: HashAlgo: named of hash
        key:bytes: if use rc4 etc. , key should be added
    '''
    if isinstance(hash_name, HashAlgo):
        hash_name = hash_name.name
    assert hasattr(hashlib, isinstance), 'no such hash algorithm'
    f = getattr(hashlib, hash_name)
    model = f()
    if isinstance(content, str):
        content = content.encode('ascii')
    model.update(content)
    return model.hexdigest()