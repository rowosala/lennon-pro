"""
Module Audio Steganography
==========================

Module ini mengimplementasikan teknik steganografi pada file audio
menggunakan metode Least Significant Bit (LSB).

Author: modo
Date: 2025
"""

import numpy as np
import soundfile as sf
import struct
from .enkripsi import AESEncryption
from .utils import convert_to_wav, validate_file, get_file_info


class AudioSteganography:
    """
    Kelas utama untuk steganografi audio menggunakan LSB
    
    Attributes:
        delimiter (bytes): Delimiter untuk menandai akhir pesan
        aes_encryption (AESEncryption): Instance untuk enkripsi AES
    """
    
    def __init__(self):
        # Delimiter khusus untuk menandai akhir pesan tersembunyi
        self.delimiter = b'<END_OF_SECRET_MESSAGE>'
        self.aes_encryption = AESEncryption()
    
    def text_to_binary(self, text: str) -> str:
        """
        Konversi teks ke representasi binary
        
        Args:
            text (str): Teks yang akan dikonversi
            
        Returns:
            str: String binary (contoh: '01001000')
            
        Penjelasan:
            - Setiap karakter dikonversi ke ASCII
            - ASCII dikonversi ke binary 8-bit
            - Hasil digabungkan menjadi string panjang
        """
        binary = ''
        for char in text:
            # Konversi karakter ke ASCII, lalu ke binary 8-bit
            binary += format(ord(char), '08b')
        return binary
    
    def binary_to_text(self, binary: str) -> str:
        """
        Konversi string binary kembali ke teks
        
        Args:
            binary (str): String binary
            
        Returns:
            str: Teks asli
            
        Penjelasan:
            - Binary dipecah per 8 bit (1 byte)
            - Setiap 8 bit dikonversi ke integer
            - Integer dikonversi ke karakter ASCII
        """
        text = ''
        for i in range(0, len(binary), 8):
            # Ambil 8 bit, konversi ke integer, lalu ke karakter
            byte = binary[i:i+8]
            if len(byte) == 8:  # Pastikan 8 bit lengkap
                text += chr(int(byte, 2))
        return text
    
    def embed_lsb(self, audio_data: np.ndarray, binary_message: str) -> np.ndarray:
        """
        Menyisipkan pesan binary ke audio menggunakan LSB
        
        Args:
            audio_data (np.ndarray): Data audio dalam format numpy array
            binary_message (str): Pesan dalam format binary
            
        Returns:
            np.ndarray: Data audio yang sudah berisi pesan tersembunyi
            
        Penjelasan:
            - LSB (Least Significant Bit) adalah bit terakhir dari setiap sample
            - Modifikasi LSB tidak mengubah kualitas audio secara signifikan
            - Setiap bit pesan mengganti 1 LSB dari sample audio
        """
        # Copy array agar tidak memodifikasi original
        stego_audio = audio_data.copy()
        
        # Flatten array jika multi-channel
        if len(stego_audio.shape) > 1:
            stego_audio_flat = stego_audio.flatten()
        else:
            stego_audio_flat = stego_audio.copy()
        
        # Convert audio ke integer untuk bit manipulation
        # Asumsi audio dalam range [-1, 1], konversi ke 16-bit integer
        audio_int = (stego_audio_flat * 32767).astype(np.int16)
        
        # Cek apakah audio cukup besar untuk menampung pesan
        if len(binary_message) > len(audio_int):
            raise Exception(f"File audio terlalu kecil! Diperlukan minimal {len(binary_message)} samples, tersedia {len(audio_int)}")
        
        # Sisipkan setiap bit pesan ke LSB audio
        for i, bit in enumerate(binary_message):
            # Ambil sample audio saat ini
            current_sample = int(audio_int[i])
            
            # Ganti LSB dengan bit pesan
            # Hapus bit terakhir (AND dengan 11111110)
            current_sample = current_sample & 0xFFFE
            
            # Tambahkan bit pesan (OR dengan bit)
            current_sample = current_sample | int(bit)
            
            # Simpan kembali
            audio_int[i] = current_sample
        
        # Convert kembali ke float range [-1, 1]
        stego_audio_flat = audio_int.astype(np.float32) / 32767.0
        
        # Reshape kembali jika perlu
        if len(stego_audio.shape) > 1:
            stego_audio = stego_audio_flat.reshape(stego_audio.shape)
        else:
            stego_audio = stego_audio_flat
        
        return stego_audio
    
    def extract_lsb(self, audio_data: np.ndarray, message_length: int = None) -> str:
        """
        Ekstrak pesan binary dari audio menggunakan LSB
        
        Args:
            audio_data (np.ndarray): Data audio yang berisi pesan tersembunyi
            message_length (int, optional): Panjang pesan yang akan diekstrak
            
        Returns:
            str: Pesan dalam format binary
            
        Penjelasan:
            - Membaca LSB dari setiap sample audio
            - Mengumpulkan bit-bit tersebut menjadi pesan binary
            - Berhenti saat delimiter ditemukan atau panjang tercapai
        """
        # Flatten array jika multi-channel
        if len(audio_data.shape) > 1:
            audio_flat = audio_data.flatten()
        else:
            audio_flat = audio_data.copy()
        
        # Convert ke integer
        audio_int = (audio_flat * 32767).astype(np.int16)
        
        # Ekstrak LSB dari setiap sample
        binary_message = ''
        max_bits = len(audio_int) if message_length is None else message_length * 8
        
        for i in range(min(max_bits, len(audio_int))):
            # Ambil LSB (bit terakhir)
            lsb = int(audio_int[i]) & 1
            binary_message += str(lsb)
        
        return binary_message
    
    def embed_message(self, audio_file: str, message: str, password: str, output_file: str = None) -> str:
        """
        Fungsi utama untuk menyisipkan pesan terenkripsi ke audio
        
        Args:
            audio_file (str): Path file audio input
            message (str): Pesan yang akan disembunyikan
            password (str): Password untuk enkripsi
            output_file (str, optional): Path file output
            
        Returns:
            str: Path file output yang berisi pesan tersembunyi
            
        Proses:
            1. Validasi file audio
            2. Konversi ke WAV jika perlu
            3. Enkripsi pesan dengan AES-128
            4. Konversi pesan terenkripsi + delimiter ke binary
            5. Sisipkan ke audio menggunakan LSB
            6. Simpan file output
        """
        try:
            print("🔐 Memulai proses penyisipan pesan...")
            
            # 1. Validasi file
            if not validate_file(audio_file):
                raise Exception("File audio tidak valid")
            
            # 2. Konversi ke WAV jika bukan WAV
            working_file = audio_file
            if not audio_file.lower().endswith('.wav'):
                print("📁 Mengkonversi file ke format WAV...")
                working_file = convert_to_wav(audio_file)
            
            # 3. Baca file audio
            print("📖 Membaca file audio...")
            audio_data, sample_rate = sf.read(working_file)
            
            # 4. Enkripsi pesan
            print("🔒 Mengenkripsi pesan...")
            encrypted_message = self.aes_encryption.encrypt(message, password)
            
            # 5. Gabungkan dengan delimiter
            full_message = encrypted_message + self.delimiter
            
            # 6. Konversi ke binary
            print("🔢 Konversi pesan ke binary...")
            binary_message = ''
            for byte in full_message:
                binary_message += format(byte, '08b')
            
            # 7. Cek kapasitas
            required_bits = len(binary_message)
            available_bits = len(audio_data.flatten()) if len(audio_data.shape) > 1 else len(audio_data)
            
            if required_bits > available_bits:
                raise Exception(f"Pesan terlalu panjang! Diperlukan {required_bits} bit, tersedia {available_bits} bit")
            
            print(f"📊 Panjang pesan: {len(message)} karakter")
            print(f"📊 Panjang terenkripsi: {len(encrypted_message)} bytes") 
            print(f"📊 Binary bits diperlukan: {required_bits}")
            print(f"📊 Kapasitas audio: {available_bits} bit")
            
            # 8. Sisipkan pesan
            print("🔧 Menyisipkan pesan ke audio...")
            stego_audio = self.embed_lsb(audio_data, binary_message)
            
            # 9. Simpan file output
            if output_file is None:
                base_name = audio_file.rsplit('.', 1)[0]
                output_file = f"{base_name}_stego.wav"
            
            print(f"💾 Menyimpan file output: {output_file}")
            sf.write(output_file, stego_audio, sample_rate)
            
            print("✅ Proses penyisipan pesan berhasil!")
            return output_file
            
        except Exception as e:
            raise Exception(f"Error dalam penyisipan pesan: {str(e)}")
    
    def extract_message(self, stego_audio_file: str, password: str) -> str:
        """
        Fungsi utama untuk mengekstrak dan mendekripsi pesan dari audio
        
        Args:
            stego_audio_file (str): Path file audio yang berisi pesan tersembunyi
            password (str): Password untuk dekripsi
            
        Returns:
            str: Pesan asli yang telah didekripsi
            
        Proses:
            1. Validasi file audio
            2. Baca file audio
            3. Ekstrak binary dari LSB
            4. Cari delimiter dan pisahkan pesan
            5. Dekripsi pesan dengan AES-128
            6. Return pesan asli
        """
        try:
            print("🔍 Memulai proses ekstraksi pesan...")
            
            # 1. Validasi file
            if not validate_file(stego_audio_file):
                raise Exception("File audio tidak valid")
            
            # 2. Baca file audio
            print("📖 Membaca file audio...")
            audio_data, sample_rate = sf.read(stego_audio_file)
            
            # 3. Ekstrak binary dari LSB
            print("🔢 Mengekstrak binary dari audio...")
            binary_data = self.extract_lsb(audio_data)
            
            # 4. Konversi binary ke bytes
            print("🔍 Mencari delimiter dalam data...")
            bytes_data = b''
            for i in range(0, len(binary_data), 8):
                byte_bits = binary_data[i:i+8]
                if len(byte_bits) == 8:
                    bytes_data += bytes([int(byte_bits, 2)])
                    
                    # Cek apakah delimiter ditemukan
                    if bytes_data.endswith(self.delimiter):
                        # Hapus delimiter dari data
                        encrypted_message = bytes_data[:-len(self.delimiter)]
                        break
            else:
                raise Exception("Delimiter tidak ditemukan. Mungkin file tidak berisi pesan atau password salah.")
            
            # 5. Dekripsi pesan
            print("🔓 Mendekripsi pesan...")
            decrypted_message = self.aes_encryption.decrypt(encrypted_message, password)
            
            print("✅ Proses ekstraksi pesan berhasil!")
            return decrypted_message
            
        except Exception as e:
            raise Exception(f"Error dalam ekstraksi pesan: {str(e)}")
    
    def get_capacity(self, audio_file: str) -> dict:
        """
        Menghitung kapasitas maksimum pesan yang bisa disimpan
        
        Args:
            audio_file (str): Path file audio
            
        Returns:
            dict: Informasi kapasitas
        """
        try:
            info = get_file_info(audio_file)
            
            # Hitung overhead (delimiter + enkripsi)
            delimiter_size = len(self.delimiter)
            encryption_overhead = 16 + 16  # IV + minimal padding
            total_overhead = delimiter_size + encryption_overhead
            
            max_bytes = info['max_message_size'] - total_overhead
            max_chars = max_bytes  # Estimasi 1 byte per karakter untuk teks biasa
            
            return {
                'max_bytes': max_bytes,
                'max_chars': max_chars,
                'total_capacity': info['max_message_size'],
                'overhead': total_overhead,
                'delimiter_size': delimiter_size,
                'encryption_overhead': encryption_overhead
            }
            
        except Exception as e:
            raise Exception(f"Error menghitung kapasitas: {str(e)}")


def test_steganography():
    """
    Fungsi testing untuk menguji steganografi audio
    """
    print("=== Testing Audio Steganography ===")
    
    # Buat instance steganografi
    stego = AudioSteganography()
    
    # Data test (sesuaikan dengan file audio yang ada)
    audio_file = "test_audio.wav"  # Ganti dengan file audio yang tersedia
    message = "Ini adalah pesan rahasia untuk testing steganografi audio dengan AES-128!"
    password = "password123"
    
    if not validate_file(audio_file):
        print("❌ File test tidak ditemukan. Letakkan file 'test_audio.wav' untuk testing.")
        return
    
    try:
        # Test kapasitas
        capacity = stego.get_capacity(audio_file)
        print(f"📊 Kapasitas maksimal: {capacity['max_chars']} karakter")
        
        # Test embed
        print(f"\n🔐 Testing embed pesan...")
        stego_file = stego.embed_message(audio_file, message, password)
        print(f"✅ Pesan berhasil disimpan di: {stego_file}")
        
        # Test extract
        print(f"\n🔍 Testing extract pesan...")
        extracted_message = stego.extract_message(stego_file, password)
        print(f"📝 Pesan asli: {message}")
        print(f"📝 Pesan extract: {extracted_message}")
        
        # Verifikasi
        if message == extracted_message:
            print("✅ Test PASSED: Steganografi berhasil!")
        else:
            print("❌ Test FAILED: Pesan tidak cocok!")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")


if __name__ == "__main__":
    test_steganography()