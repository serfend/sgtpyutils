from Crypto.Cipher import Blowfish
from .utils import padding_to


def test_Blowfish(key, iv, content):
    # MODE_CBC
    e = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_CBC,
                     padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_CBC,
                     padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_CFB
    e = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_CFB,
                     padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_CFB,
                     padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_ECB no need for iv
    e = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_ECB).encrypt(
        padding_to(content, 8))
    d = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_ECB).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')
    # MODE_OFB
    e = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_OFB,
                     padding_to(iv, 8, 8)).encrypt(padding_to(content, 8))
    d = Blowfish.new(padding_to(key, 32, 32), Blowfish.MODE_OFB,
                     padding_to(iv, 8, 8)).decrypt(e)
    print(f'e = {e}\nd = {d}\n\n')


def main():
    config = {
        "key": "SGTSerfend2022",
        "iv": "1Ssecret1Ssecret1Ssecret"
    }
    content = ('0123456789abcdefAAAAAAAAAA'*5).encode()
    iv = str(config['iv']).encode()
    key = str(config['key']).encode()
    test_Blowfish(key, iv, content)
