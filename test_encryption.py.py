# encryption.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class EncryptionLayer:
    """AES-256 encryption for secure communication."""
    def __init__(self):
        self.key = get_random_bytes(32)
        self.iv = get_random_bytes(16)

    def encrypt(self, data):
        """Encrypt data."""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(data.encode(), AES.block_size))

    def decrypt(self, encrypted_data):
        """Decrypt data."""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()
