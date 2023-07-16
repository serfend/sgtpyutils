from sgtpyutils.hash import *

raw_md5 = 'e10adc3949ba59abbe56e057f20f883e'
raw_sha256 = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
raw = '123456'


def test_hash():
    assert get_hash(raw, HashAlgo.md5) == raw_md5
    assert get_hash(raw, HashAlgo.sha256) == raw_sha256


def test_hash_crash():
    assert brute_hash(
      target=raw_sha256, 
      hash_name=HashAlgo.sha256,
      brute_length=6,
      table='1234567890'
    ) == raw
