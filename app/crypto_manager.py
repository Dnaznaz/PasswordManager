from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import hashlib
import binascii
import os

MASTER_PASSWORD = ''
SALT = ''

def hash_password(uPass, salt):
    '''DOC'''

    return binascii.hexlify(hashlib.pbkdf2_hmac(
        hash_name='sha512',
        password=uPass,
        salt=salt,
        iterations=200000,
        ))

def encrypt_symm(auth_pass, data, iv):
    '''DOC'''

    key = str.encode(_padd(auth_pass))
    cipher = AES.new(key, AES.MODE_EAX, iv)

    ciphertext, tag = cipher.encrypt_and_digest(str.encode(data))

    hexCiphertext = binascii.hexlify(ciphertext)
    hexTag = binascii.hexlify(tag)
    joint = hexCiphertext.decode() + ":" + hexTag.decode()

    return joint

def decrypt_symm(auth_pass, enc_data, iv):
    '''DOC'''

    key = str.encode(_padd(auth_pass))
    cipher = AES.new(key, AES.MODE_EAX, iv)

    hexCiphertext, hexTag = enc_data.split(':')

    ciphertext = binascii.unhexlify(str.encode(hexCiphertext))
    tag = binascii.unhexlify(str.encode(hexTag))

    data = cipher.decrypt_and_verify(ciphertext, tag)

    return data

def get_iv():
    return get_random_bytes(16)

def encrypt_asymm(auth_pass, data):
    '''DOC'''

    rsaKey = RSA.import_key(auth_pass)
    sessionKey = get_random_bytes(16)

    cipherRSA = PKCS1_OAEP.new(rsaKey)
    encSessionKey = cipherRSA.encrypt(sessionKey)

    cipherAES = AES.new(sessionKey, AES.MODE_EAX)
    ciphertext, tag = cipherAES.encrypt_and_digest(data)

    msg = "{sessionKey},{vi},{tag},{ciphertext}".format(
        sessionKey = binascii.hexlify(encSessionKey).decode(),
        vi = binascii.hexlify(cipherAES.nonce).decode(),
        tag = binascii.hexlify(tag).decode(),
        ciphertext = binascii.hexlify(ciphertext).decode()
        )

    return msg

def decrypt_asymm(auth_pass, enc_data):
    '''DOC'''

    encSessionKey, vi, tag, ciphertext = list(map(lambda x: binascii.unhexlify(str.encode(x)), enc_data.split(",")))

    cipherRSA = PKCS1_OAEP.new(auth_pass)
    sessionKey = cipherRSA.decrypt(encSessionKey)

    cipherAES = AES.new(sessionKey, AES.MODE_EAX, vi)
    data = cipherAES.decrypt_and_verify(ciphertext, tag)

    return tag

def generate_comm_keys():
    code = os.urandom(16).decode()
    key = RSA.generate(2048)

    privateKey = key.exportKey(passphrase=code, pkcs=8, protection='scryptAndAES128-CBC')
    publicKey = key.publickey.exportKey()

    return (privateKey, publicKey)

def authorize(auth_pass):
    '''DOC'''

    if MASTER_PASSWORD == '':
        return True

    return MASTER_PASSWORD == hash_password(auth_pass, SALT).decode()

def _padd(text):
    '''DOC'''

    n = 16 - (len(text) % 16)

    return text + (' ' * n)
