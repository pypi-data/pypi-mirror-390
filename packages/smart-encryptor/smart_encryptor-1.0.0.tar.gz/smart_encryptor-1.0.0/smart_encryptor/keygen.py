from cryptography.fernet import Fernet

def generate_key(save_to_file: str = None) -> str:
    """
    Generates a new encryption key and optionally saves it to a file.
    Returns the key as a string.
    """
    key = Fernet.generate_key().decode()
    if save_to_file:
        with open(save_to_file, "w") as f:
            f.write(key)
    return key
