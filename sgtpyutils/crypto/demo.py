from Crypto.Cipher import AES, DES, DES3
from .utils import padding_to
from . import demo_3des, demo_aes, demo_blowfish, demo_des, demo_rsa


def main():
    key = bytes.fromhex('e738989a5bcb3c93a1101010')
    content = bytes.fromhex(
        '0c55dc63af806636fbc3bc81051c279c92ec9a6607aedaa877018cf4dbcc53cb2d')
    print(AES.new(padding_to(key, 32, 32), AES.MODE_ECB).decrypt(
        padding_to(content, 16)))
    config = {
        "key": "SGTSerfend2022",
        "iv": "1Ssecret1Ssecret1Ssecret"
    }
    content = ('0123456789abcdefAAAAAAAAAA'*5).encode()
    iv = str(config['iv']).encode()
    key = str(config['key']).encode()
    demo_des.main(key, iv, content)
    print('-'*20)
    demo_3des.main(key, iv, content)
    print('-'*20)
    demo_aes.main(key, iv, content)
    print('-'*20)
    demo_rsa.main(content)
    print('-'*20)
    demo_blowfish.main()


if __name__ == '__main__':
    main()
