from Crypto.Cipher import AES, DES, DES3
from .utils import padding_to


def main(key: bytes, iv: bytes, content: bytes):
    # MODE_CBC
    e = DES3.new(padding_to(key, 24, 24), DES3.MODE_CBC,
                 padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES3.new(padding_to(key, 24, 24), DES3.MODE_CBC,
                 padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_CFB
    e = DES3.new(padding_to(key, 24, 24), DES3.MODE_CFB,
                 padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES3.new(padding_to(key, 24, 24), DES3.MODE_CFB,
                 padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_ECB no need for iv
    e = DES3.new(padding_to(key, 24, 24), DES3.MODE_ECB).encrypt(
        padding_to(content, 8))
    d = DES3.new(padding_to(key, 24, 24), DES3.MODE_ECB).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_OFB
    e = DES3.new(padding_to(key, 24, 24), DES3.MODE_OFB,
                 padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES3.new(padding_to(key, 24, 24), DES3.MODE_OFB,
                 padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
