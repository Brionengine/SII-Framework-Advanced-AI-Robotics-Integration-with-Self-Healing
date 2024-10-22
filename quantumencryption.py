from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Generate a random key for AES-256
key = get_random_bytes(32)  # 32 bytes = 256 bits
iv = get_random_bytes(16)  # Initialization vector

def encrypt_data(data):
    """Encrypt data using AES-256."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return encrypted

def decrypt_data(encrypted_data):
    """Decrypt AES-256 encrypted data."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted.decode()

# Test the encryption and decryption
encrypted = encrypt_data("Confidential message")
print(f"Encrypted: {encrypted}")

decrypted = decrypt_data(encrypted)
print(f"Decrypted: {decrypted}")
