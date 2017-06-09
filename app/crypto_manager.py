from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib

def hashPassword(uPass, salt):
    return hashlib.pbkdf2_hmac(hash_name='sha512', password=uPass, salt=salt, iterations=100000)

def encrypt_symm(auth_pass, data):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    print(tag)
    print(ciphertext)
    print(cipher.nonce)

def decrypt_symm(auth_pass, enc_data):
    pass

def encrypt_asymm(auth_pass, data):
    pass

def decrypt_asymm(auth_pass, enc_data):
    pass

def authorize(auth_pass):
    pass