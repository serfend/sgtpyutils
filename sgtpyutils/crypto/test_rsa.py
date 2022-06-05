
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.Hash import SHA


def main(content: bytes):
    rsa = RSA.generate(2048)
    public_key = rsa.public_key().export_key()
    private_key = rsa.export_key()
    print(f'public_key: {public_key}\n\nprivate_key: {private_key}\n')
    private_key = RSA.importKey(private_key)
    public_key = RSA.importKey(public_key)

    # sign a message
    signer = PKCS1_signature.new(private_key)
    digest = SHA.new()
    digest.update(content)
    sign = signer.sign(digest)
    print(f'sign: {sign}\n')

    # check sign for a message
    verifier = PKCS1_signature.new(public_key)
    digest = SHA.new()
    digest.update(content)
    sign_result = verifier.verify(digest, sign)
    print(f'the message check sign result is :{sign_result}\n')

    # encrypt rsa
    cipher = PKCS1_cipher.new(public_key)
    encrypt_text = cipher.encrypt(content)
    print(f'encrypt_text: {encrypt_text}\n')

    # decrypt rsa
    cipher = PKCS1_cipher.new(private_key)
    decrypt_text = cipher.decrypt(encrypt_text, b'')
    print(f'decrypt_text: {decrypt_text}\n')
