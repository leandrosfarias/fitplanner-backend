# encryption.py
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


def derive_key(master_password: str, encryption_salt: str) -> bytes:
    """Deriva uma chave segura a partir da senha mestra e do salt."""
    password_bytes = master_password.encode('utf-8')
    salt_bytes = encryption_salt.encode('utf-8')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,

        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key


def encrypt_data(data_to_encrypt: str, key: bytes) -> str:
    """Criptografa uma string usando uma chave Fernet."""
    f = Fernet(key)
    encrypted_data = f.encrypt(data_to_encrypt.encode('utf-8'))
    return encrypted_data.decode('utf-8')


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Descriptografa uma string usando uma chave Fernet."""
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_data.encode('utf-8'))
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Erro ao descriptografar: {e}")
        return None
