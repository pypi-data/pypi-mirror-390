from smart_encryptor import encrypt, decrypt, generate_key, SmartEncryptor

def test_aes_encryption():
    key_b64 = generate_key()
    import base64
    key = base64.urlsafe_b64decode(key_b64)
    text = "secure message"
    token = encrypt(text, key)
    assert decrypt(token, key) == text

def test_fernet_encryption():
    enc = SmartEncryptor()
    msg = "test123"
    token = enc.encrypt(msg)
    assert enc.decrypt(token) == msg
