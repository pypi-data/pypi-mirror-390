import os
import base64

DEFAULT_ENV_KEY = "SMART_ENCRYPTOR_KEY"

def get_default_key() -> bytes:
    """
    Retrieve or generate a persistent AES-256 key.
    """
    key_b64 = os.getenv(DEFAULT_ENV_KEY)
    if not key_b64:
        # Generate a new random 32-byte key
        key = os.urandom(32)
        key_b64 = base64.urlsafe_b64encode(key).decode()
        # For dev, you can store it in .env or print it
        print(f"[smart-encryptor] Generated new key (store it securely): {key_b64}")
        return key
    return base64.urlsafe_b64decode(key_b64.encode())

def set_key_in_env(key: bytes):
    """
    Optionally set encryption key at runtime.
    """
    os.environ[DEFAULT_ENV_KEY] = base64.urlsafe_b64encode(key).decode()
