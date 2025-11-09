import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .keymanager import get_default_key
from cryptography.fernet import Fernet 

def encrypt(plaintext: str, key: bytes = None) -> str:
    """
    Encrypt plaintext using AES-256-GCM.
    """
    if not plaintext:
        raise ValueError("Plaintext cannot be empty.")

    key = key or get_default_key()
    if len(key) != 32:
        raise ValueError("Encryption key must be 32 bytes (256 bits).")

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    combined = nonce + ciphertext
    return base64.urlsafe_b64encode(combined).decode()

def decrypt(token: str, key: bytes = None) -> str:
    """
    Decrypt ciphertext using AES-256-GCM.
    """
    key = key or get_default_key()
    if len(key) != 32:
        raise ValueError("Decryption key must be 32 bytes (256 bits).")

    aesgcm = AESGCM(key)
    data = base64.urlsafe_b64decode(token)
    nonce, ciphertext = data[:12], data[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()




class SmartEncryptor:
    def __init__(self, key: str = None):
        # Use default fallback key if not provided (for dev/demo only)
        if key is None:
            key = base64.urlsafe_b64encode(b"default_smart_encryptor_key_32bytes!")[:44].decode()
        self.key = key
        self.fernet = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """
        Encrypt plain text and return encrypted string.
        """
        if not isinstance(data, str):
            raise TypeError("Data must be a string.")
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        """
        Decrypt previously encrypted string.
        """
        if not isinstance(token, str):
            raise TypeError("Token must be a string.")
        return self.fernet.decrypt(token.encode()).decode()

