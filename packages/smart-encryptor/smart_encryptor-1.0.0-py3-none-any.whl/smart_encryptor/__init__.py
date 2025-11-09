"""
smart-encryptor
---------------
Secure AES-256-GCM & Fernet-based encryption/decryption package.
"""

from .core import encrypt, decrypt, SmartEncryptor
from .keymanager import get_default_key, set_key_in_env
from .keygen import generate_key

__all__ = [
    "encrypt",
    "decrypt",
    "get_default_key",
    "set_key_in_env",
    "SmartEncryptor",
    "generate_key",
]

__version__ = "1.0.0"
