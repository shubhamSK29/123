# crypto.py
import os
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key_argon2id(master_password: str, salt: bytes) -> bytes:
    time_cost = 3
    memory_cost = 65536
    parallelism = 1
    key_length = 32
    return hash_secret_raw(
        secret=master_password.encode('utf-8'),
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=key_length,
        type=Type.ID
    )

def encrypt_password_aes_gcm(password: str, master_password: str) -> tuple:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key_argon2id(master_password, salt)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, password.encode('utf-8'), None)
    return salt, nonce, ciphertext_with_tag

def decrypt_password_aes_gcm(salt: bytes, nonce: bytes, ciphertext_with_tag: bytes, master_password: str) -> str:
    key = derive_key_argon2id(master_password, salt)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return plaintext.decode('utf-8')

