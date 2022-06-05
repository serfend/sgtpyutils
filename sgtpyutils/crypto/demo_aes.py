from Crypto.Cipher import AES, DES, DES3
from .utils import padding_to


def main(key: bytes, iv: bytes, content: bytes):
    # MODE_CBC
    e = AES.new(padding_to(key, 32, 32), AES.MODE_CBC, padding_to(
        iv, 16, 16)).encrypt(padding_to(content, 16))
    d = AES.new(padding_to(key, 32, 32), AES.MODE_CBC,
                padding_to(iv, 16, 16)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_CFB
    e = AES.new(padding_to(key, 32, 32), AES.MODE_CFB, padding_to(
        iv, 16, 16)).encrypt(padding_to(content, 16))
    d = AES.new(padding_to(key, 32, 32), AES.MODE_CFB,
                padding_to(iv, 16, 16)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_ECB no need for iv
    e = AES.new(padding_to(key, 32, 32), AES.MODE_ECB).encrypt(
        padding_to(content, 16))
    d = AES.new(padding_to(key, 32, 32), AES.MODE_ECB).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_OFB
    e = AES.new(padding_to(key, 32, 32), AES.MODE_OFB, padding_to(
        iv, 16, 16)).encrypt(padding_to(content, 16))
    d = AES.new(padding_to(key, 32, 32), AES.MODE_OFB,
                padding_to(iv, 16, 16)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
