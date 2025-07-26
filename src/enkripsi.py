"""
Module Enkripsi AES-128
=======================

Module ini berisi implementasi enkripsi dan dekripsi menggunakan 
Advanced Encryption Standard (AES) dengan kunci 128-bit.

Author: modo
Date: 2025
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class AESEncryption:
    """
    Kelas untuk enkripsi dan dekripsi AES-128
    
    Attributes:
        key_size (int): Ukuran kunci dalam bytes (16 untuk AES-128)
        block_size (int): Ukuran blok AES dalam bytes (16)
    """
    
    def __init__(self):
        self.key_size = 16  # 128 bits = 16 bytes
        self.block_size = 16  # AES block size = 16 bytes
    
    def generate_key(self, password: str) -> bytes:
        """
        Generate kunci AES dari password menggunakan SHA-256
        
        Args:
            password (str): Password yang akan dijadikan kunci
            
        Returns:
            bytes: Kunci AES 128-bit (16 bytes)
            
        Penjelasan:
            - Menggunakan SHA-256 untuk hash password
            - Mengambil 16 bytes pertama untuk AES-128
            - Memberikan konsistensi kunci dari password yang sama
        """
        # Hash password menggunakan SHA-256
        hash_obj = hashlib.sha256(password.encode('utf-8'))
        # Ambil 16 bytes pertama untuk AES-128
        return hash_obj.digest()[:self.key_size]
    
    def encrypt(self, plaintext: str, password: str) -> bytes:
        """
        Enkripsi teks menggunakan AES-128 dalam mode CBC
        
        Args:
            plaintext (str): Teks yang akan dienkripsi
            password (str): Password untuk generate kunci
            
        Returns:
            bytes: Data terenkripsi (IV + ciphertext)
            
        Penjelasan:
            - Menggunakan mode CBC (Cipher Block Chaining)
            - IV (Initialization Vector) di-generate secara random
            - Padding PKCS7 untuk memastikan ukuran blok yang tepat
            - Format output: IV (16 bytes) + encrypted_data
        """
        try:
            # Generate kunci dari password
            key = self.generate_key(password)
            
            # Generate random IV (Initialization Vector)
            iv = os.urandom(self.block_size)
            
            # Convert string ke bytes
            plaintext_bytes = plaintext.encode('utf-8')
            
            # Setup padding PKCS7
            padder = padding.PKCS7(self.block_size * 8).padder()
            padded_data = padder.update(plaintext_bytes)
            padded_data += padder.finalize()
            
            # Setup cipher dengan mode CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Lakukan enkripsi
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Gabungkan IV dan ciphertext
            return iv + ciphertext
            
        except Exception as e:
            raise Exception(f"Error dalam enkripsi: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, password: str) -> str:
        """
        Dekripsi data yang telah dienkripsi dengan AES-128
        
        Args:
            encrypted_data (bytes): Data terenkripsi (IV + ciphertext)
            password (str): Password untuk generate kunci
            
        Returns:
            str: Teks asli yang telah didekripsi
            
        Penjelasan:
            - Ekstrak IV dari 16 bytes pertama
            - Ambil ciphertext dari sisanya
            - Gunakan kunci yang sama untuk dekripsi
            - Remove padding dan convert ke string
        """
        try:
            # Generate kunci yang sama dari password
            key = self.generate_key(password)
            
            # Ekstrak IV dan ciphertext
            iv = encrypted_data[:self.block_size]
            ciphertext = encrypted_data[self.block_size:]
            
            # Setup cipher untuk dekripsi
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Lakukan dekripsi
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            unpadder = padding.PKCS7(self.block_size * 8).unpadder()
            plaintext_bytes = unpadder.update(padded_plaintext)
            plaintext_bytes += unpadder.finalize()
            
            # Convert bytes ke string
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error dalam dekripsi: {str(e)}")


def test_encryption():
    """
    Fungsi testing untuk memastikan enkripsi dan dekripsi bekerja dengan benar
    """
    aes = AESEncryption()
    
    # Test data
    message = "Ini adalah pesan rahasia untuk testing AES-128!"
    password = "password123"
    
    print("=== Testing AES Encryption ===")
    print(f"Original message: {message}")
    print(f"Password: {password}")
    
    # Enkripsi
    encrypted = aes.encrypt(message, password)
    print(f"Encrypted length: {len(encrypted)} bytes")
    print(f"Encrypted (hex): {encrypted.hex()[:50]}...")
    
    # Dekripsi
    decrypted = aes.decrypt(encrypted, password)
    print(f"Decrypted message: {decrypted}")
    
    # Verifikasi
    if message == decrypted:
        print("✓ Test PASSED: Enkripsi dan dekripsi berhasil!")
    else:
        print("✗ Test FAILED: Ada kesalahan dalam proses enkripsi/dekripsi")


if __name__ == "__main__":
    test_encryption()