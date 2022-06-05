from Crypto.Cipher import AES, DES, DES3
from .utils import padding_to


def main(key: bytes, iv: bytes, content: bytes):
    # MODE_CBC
    e = DES.new(padding_to(key, 8, 8), DES.MODE_CBC, padding_to(
        iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES.new(padding_to(key, 8, 8), DES.MODE_CBC,
                padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_CFB
    e = DES.new(padding_to(key, 8, 8), DES.MODE_CFB, padding_to(
        iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES.new(padding_to(key, 8, 8), DES.MODE_CFB,
                padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_ECB no need for iv
    e = DES.new(padding_to(key, 8, 8), DES.MODE_ECB).encrypt(
        padding_to(content, 8))
    d = DES.new(padding_to(key, 8, 8), DES.MODE_ECB).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_OFB
    e = DES.new(padding_to(key, 8, 8), DES.MODE_OFB, padding_to(
        iv, 8, 8)).encrypt(padding_to(content, 8))
    d = DES.new(padding_to(key, 8, 8), DES.MODE_OFB,
                padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
