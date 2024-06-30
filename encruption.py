import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives import padding
# pip install cryptography

class Encrypt:
    def __init__(self, password: str):
        self.password = password.encode()  # Password should be securely managed
        self.key = None
        self.salt = None

    # Function to derive the encryption key from a password using PBKDF2
    def derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    # Function to generate a key and save it to a file
    def generate_key(self, location="secret.key"):
        self.salt = os.urandom(16)  # Generate a 128-bit salt
        self.key = self.derive_key(self.salt)
        with open(location, "wb") as key_file:
            key_file.write(self.salt)  # Save the salt to the file

    # Function to load the key from a file
    def load_key(self, location="secret.key"):
        try:
            with open(location, "rb") as key_file:
                self.salt = key_file.read(16)  # Read the salt from the file
            self.key = self.derive_key(self.salt)
        except Exception as e:
            print(f"Error loading key: {e}")
            self.key = None

    # Function to generate a checksum for the data
    def generate_checksum(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    # Function to encrypt data with AES and checksum
    def encrypt_data(self, data):
        if self.key is None:
            raise ValueError("Encryption key is not loaded. Please load or generate a key first.")
        
        # Generate checksum
        checksum = self.generate_checksum(data)
        
        # Concatenate data and checksum
        data_with_checksum = f"{data}|{checksum}".encode()
        
        # AES encryption
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Padding data
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data_with_checksum) + padder.finalize()
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and encrypted data
        encrypted_message = iv + encrypted_data
        return urlsafe_b64encode(encrypted_message)

    # Function to decrypt data and verify checksum
    def decrypt_data(self, encrypted_data):
        if self.key is None:
            raise ValueError("Encryption key is not loaded. Please load or generate a key first.")
        
        encrypted_data = urlsafe_b64decode(encrypted_data)
        
        # Extract IV
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        
        # AES decryption
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt and unpad data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data_with_checksum = unpadder.update(padded_data) + unpadder.finalize()
        
        # Separate data and checksum
        data_with_checksum = data_with_checksum.decode()
        data, checksum = data_with_checksum.rsplit('|', 1)
        
        # Verify checksum
        if self.generate_checksum(data) != checksum:
            raise ValueError("Data integrity check failed. The data may have been tampered with.")
        
        return data
