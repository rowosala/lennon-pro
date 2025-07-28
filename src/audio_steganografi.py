"""
Module Audio Steganography
==========================

Module ini mengimplementasikan teknik steganografi pada file audio
menggunakan metode Least Significant Bit (LSB) dengan fitur analisis kualitas
dan pengujian ketahanan.

Author: modo
Date: 2025
"""

import numpy as np
import soundfile as sf
import struct
import os
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
        """
        binary = ''
        for char in text:
            binary += format(ord(char), '08b')
        return binary
    
    def binary_to_text(self, binary: str) -> str:
        """
        Konversi string binary kembali ke teks
        
        Args:
            binary (str): String binary
            
        Returns:
            str: Teks asli
        """
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text
    
    def calculate_psnr(self, original: np.ndarray, modified: np.ndarray) -> float:
        """
        Menghitung Peak Signal-to-Noise Ratio (PSNR) antara audio asli dan termodifikasi
        
        Args:
            original (np.ndarray): Audio asli
            modified (np.ndarray): Audio yang telah dimodifikasi
            
        Returns:
            float: Nilai PSNR dalam dB
        """
        # Pastikan kedua array memiliki ukuran yang sama
        min_len = min(len(original), len(modified))
        original = original[:min_len]
        modified = modified[:min_len]
        
        # Hitung MSE (Mean Squared Error)
        mse = np.mean((original - modified) ** 2)
        
        if mse == 0:
            return float('inf')  # Tidak ada perbedaan
        
        # Hitung PSNR
        max_pixel_value = 1.0  # Untuk audio normalized [-1, 1]
        psnr = 20 * np.log10(max_pixel_value / np.sqrt(mse))
        
        return psnr
    
    def calculate_mse(self, original: np.ndarray, modified: np.ndarray) -> float:
        """
        Menghitung Mean Squared Error (MSE) antara audio asli dan termodifikasi
        
        Args:
            original (np.ndarray): Audio asli
            modified (np.ndarray): Audio yang telah dimodifikasi
            
        Returns:
            float: Nilai MSE
        """
        min_len = min(len(original), len(modified))
        original = original[:min_len]
        modified = modified[:min_len]
        
        mse = np.mean((original - modified) ** 2)
        return mse
    
    def calculate_snr(self, original: np.ndarray, modified: np.ndarray) -> float:
        """
        Menghitung Signal-to-Noise Ratio (SNR)
        
        Args:
            original (np.ndarray): Audio asli
            modified (np.ndarray): Audio yang telah dimodifikasi
            
        Returns:
            float: Nilai SNR dalam dB
        """
        min_len = min(len(original), len(modified))
        original = original[:min_len]
        modified = modified[:min_len]
        
        signal_power = np.mean(original ** 2)
        noise_power = np.mean((original - modified) ** 2)
        
        if noise_power == 0:
            return float('inf')
        
        snr = 10 * np.log10(signal_power / noise_power)
        return snr
    
    def embed_lsb(self, audio_data: np.ndarray, binary_message: str) -> np.ndarray:
        """
        Menyisipkan pesan binary ke audio menggunakan LSB
        
        Args:
            audio_data (np.ndarray): Data audio dalam format numpy array
            binary_message (str): Pesan dalam format binary
            
        Returns:
            np.ndarray: Data audio yang sudah berisi pesan tersembunyi
        """
        stego_audio = audio_data.copy()
        
        if len(stego_audio.shape) > 1:
            stego_audio_flat = stego_audio.flatten()
        else:
            stego_audio_flat = stego_audio.copy()
        
        # Convert audio ke integer untuk bit manipulation
        audio_int = (stego_audio_flat * 32767).astype(np.int16)
        
        if len(binary_message) > len(audio_int):
            raise Exception(f"File audio terlalu kecil! Diperlukan minimal {len(binary_message)} samples, tersedia {len(audio_int)}")
        
        # Sisipkan setiap bit pesan ke LSB audio
        for i, bit in enumerate(binary_message):
            current_sample = int(audio_int[i])
            current_sample = current_sample & 0xFFFE
            current_sample = current_sample | int(bit)
            audio_int[i] = current_sample
        
        # Convert kembali ke float range [-1, 1]
        stego_audio_flat = audio_int.astype(np.float32) / 32767.0
        
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
        """
        if len(audio_data.shape) > 1:
            audio_flat = audio_data.flatten()
        else:
            audio_flat = audio_data.copy()
        
        audio_int = (audio_flat * 32767).astype(np.int16)
        
        binary_message = ''
        max_bits = len(audio_int) if message_length is None else message_length * 8
        
        for i in range(min(max_bits, len(audio_int))):
            lsb = int(audio_int[i]) & 1
            binary_message += str(lsb)
        
        return binary_message
    
    def add_noise(self, audio_data: np.ndarray, noise_level: float = 0.01) -> np.ndarray:
        """
        Menambahkan noise ke audio untuk pengujian ketahanan
        
        Args:
            audio_data (np.ndarray): Data audio
            noise_level (float): Level noise (0.0 - 1.0)
            
        Returns:
            np.ndarray: Audio dengan noise
        """
        noise = np.random.normal(0, noise_level, audio_data.shape)
        noisy_audio = audio_data + noise
        
        # Clamp ke range [-1, 1]
        noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
        
        return noisy_audio
    
    def compress_audio(self, audio_data: np.ndarray, sample_rate: int, compression_ratio: float = 0.5) -> np.ndarray:
        """
        Simulasi kompresi audio untuk pengujian ketahanan
        
        Args:
            audio_data (np.ndarray): Data audio
            sample_rate (int): Sample rate audio
            compression_ratio (float): Rasio kompresi (0.0 - 1.0)
            
        Returns:
            np.ndarray: Audio yang telah dikompres
        """
        # Simulasi kompresi dengan mengurangi bit depth
        bit_reduction = int(16 * (1 - compression_ratio))
        scale_factor = 2 ** bit_reduction
        
        compressed = np.round(audio_data * scale_factor) / scale_factor
        return compressed
    
    def test_robustness(self, stego_audio: np.ndarray, sample_rate: int, password: str, 
                       original_message: str) -> dict:
        """
        Menguji ketahanan steganografi terhadap berbagai serangan
        
        Args:
            stego_audio (np.ndarray): Audio dengan pesan tersembunyi
            sample_rate (int): Sample rate audio
            password (str): Password untuk dekripsi
            original_message (str): Pesan asli untuk verifikasi
            
        Returns:
            dict: Hasil pengujian ketahanan
        """
        results = {
            'original': {'success': False, 'message': '', 'error': ''},
            'noise_low': {'success': False, 'message': '', 'error': ''},
            'noise_medium': {'success': False, 'message': '', 'error': ''},
            'noise_high': {'success': False, 'message': '', 'error': ''},
            'compression_light': {'success': False, 'message': '', 'error': ''},
            'compression_heavy': {'success': False, 'message': '', 'error': ''}
        }
        
        # Test 1: Audio asli (tanpa modifikasi)
        try:
            message = self._extract_from_array(stego_audio, password)
            results['original']['success'] = (message == original_message)
            results['original']['message'] = message
        except Exception as e:
            results['original']['error'] = str(e)
        
        # Test 2: Noise rendah (0.5%)
        try:
            noisy_audio = self.add_noise(stego_audio, 0.005)
            message = self._extract_from_array(noisy_audio, password)
            results['noise_low']['success'] = (message == original_message)
            results['noise_low']['message'] = message
        except Exception as e:
            results['noise_low']['error'] = str(e)
        
        # Test 3: Noise sedang (1%)
        try:
            noisy_audio = self.add_noise(stego_audio, 0.01)
            message = self._extract_from_array(noisy_audio, password)
            results['noise_medium']['success'] = (message == original_message)
            results['noise_medium']['message'] = message
        except Exception as e:
            results['noise_medium']['error'] = str(e)
        
        # Test 4: Noise tinggi (2%)
        try:
            noisy_audio = self.add_noise(stego_audio, 0.02)
            message = self._extract_from_array(noisy_audio, password)
            results['noise_high']['success'] = (message == original_message)
            results['noise_high']['message'] = message
        except Exception as e:
            results['noise_high']['error'] = str(e)
        
        # Test 5: Kompresi ringan
        try:
            compressed_audio = self.compress_audio(stego_audio, sample_rate, 0.2)
            message = self._extract_from_array(compressed_audio, password)
            results['compression_light']['success'] = (message == original_message)
            results['compression_light']['message'] = message
        except Exception as e:
            results['compression_light']['error'] = str(e)
        
        # Test 6: Kompresi berat
        try:
            compressed_audio = self.compress_audio(stego_audio, sample_rate, 0.5)
            message = self._extract_from_array(compressed_audio, password)
            results['compression_heavy']['success'] = (message == original_message)
            results['compression_heavy']['message'] = message
        except Exception as e:
            results['compression_heavy']['error'] = str(e)
        
        return results
    
    def _extract_from_array(self, audio_data: np.ndarray, password: str) -> str:
        """
        Helper function untuk ekstrak pesan dari array audio
        
        Args:
            audio_data (np.ndarray): Data audio
            password (str): Password untuk dekripsi
            
        Returns:
            str: Pesan yang diekstrak
        """
        binary_data = self.extract_lsb(audio_data)
        
        bytes_data = b''
        for i in range(0, len(binary_data), 8):
            byte_bits = binary_data[i:i+8]
            if len(byte_bits) == 8:
                bytes_data += bytes([int(byte_bits, 2)])
                
                if bytes_data.endswith(self.delimiter):
                    encrypted_message = bytes_data[:-len(self.delimiter)]
                    break
        else:
            raise Exception("Delimiter tidak ditemukan")
        
        decrypted_message = self.aes_encryption.decrypt(encrypted_message, password)
        return decrypted_message
    
    def embed_message(self, audio_file: str, message: str, password: str, 
                     output_file: str = None, output_format: str = 'wav',
                     analyze_quality: bool = True) -> dict:
        """
        Fungsi utama untuk menyisipkan pesan terenkripsi ke audio
        
        Args:
            audio_file (str): Path file audio input
            message (str): Pesan yang akan disembunyikan
            password (str): Password untuk enkripsi
            output_file (str, optional): Path file output
            output_format (str): Format output ('wav', 'flac', 'mp3')
            analyze_quality (bool): Apakah melakukan analisis kualitas
            
        Returns:
            dict: Informasi hasil embedding termasuk analisis kualitas
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
            original_audio, sample_rate = sf.read(working_file)
            
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
            available_bits = len(original_audio.flatten()) if len(original_audio.shape) > 1 else len(original_audio)
            
            if required_bits > available_bits:
                raise Exception(f"Pesan terlalu panjang! Diperlukan {required_bits} bit, tersedia {available_bits} bit")
            
            print(f"📊 Panjang pesan: {len(message)} karakter")
            print(f"📊 Panjang terenkripsi: {len(encrypted_message)} bytes") 
            print(f"📊 Binary bits diperlukan: {required_bits}")
            print(f"📊 Kapasitas audio: {available_bits} bit")
            
            # 8. Sisipkan pesan
            print("🔧 Menyisipkan pesan ke audio...")
            stego_audio = self.embed_lsb(original_audio, binary_message)
            
            # 9. Tentukan file output
            if output_file is None:
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                output_file = f"output/{base_name}_stego.{output_format}"
            
            # 10. Simpan file output
            print(f"💾 Menyimpan file output: {output_file}")
            
            # Pastikan direktori output ada
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            if output_format.lower() == 'wav':
                sf.write(output_file, stego_audio, sample_rate)
            elif output_format.lower() == 'flac':
                sf.write(output_file, stego_audio, sample_rate, format='FLAC')
            elif output_format.lower() == 'mp3':
                # Untuk MP3, simpan sebagai WAV dulu lalu konversi
                temp_wav = output_file.replace('.mp3', '_temp.wav')
                sf.write(temp_wav, stego_audio, sample_rate)
                
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_wav(temp_wav)
                audio_segment.export(output_file, format="mp3", bitrate="192k")
                os.remove(temp_wav)
            else:
                sf.write(output_file, stego_audio, sample_rate)
            
            # 11. Analisis kualitas
            result = {
                'output_file': output_file,
                'message_length': len(message),
                'encrypted_length': len(encrypted_message),
                'binary_bits': required_bits,
                'capacity_used': (required_bits / available_bits) * 100,
                'format': output_format.upper()
            }
            
            if analyze_quality:
                print("📊 Menganalisis kualitas audio...")
                
                # Hitung metrik kualitas
                psnr = self.calculate_psnr(original_audio, stego_audio)
                mse = self.calculate_mse(original_audio, stego_audio)
                snr = self.calculate_snr(original_audio, stego_audio)
                
                result['quality_metrics'] = {
                    'psnr_db': round(psnr, 2),
                    'mse': round(mse, 8),
                    'snr_db': round(snr, 2)
                }
                
                print(f"📊 PSNR: {psnr:.2f} dB")
                print(f"📊 MSE: {mse:.8f}")
                print(f"📊 SNR: {snr:.2f} dB")
            
            print("✅ Proses penyisipan pesan berhasil!")
            return result
            
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
        """
        try:
            print("🔍 Memulai proses ekstraksi pesan...")
            
            # 1. Validasi file
            if not validate_file(stego_audio_file):
                raise Exception("File audio tidak valid")
            
            # 2. Baca file audio
            print("📖 Membaca file audio...")
            audio_data, sample_rate = sf.read(stego_audio_file)
            
            # 3. Ekstrak pesan
            message = self._extract_from_array(audio_data, password)
            
            print("✅ Proses ekstraksi pesan berhasil!")
            return message
            
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
        
        # Test embed dengan analisis kualitas
        print(f"\n🔐 Testing embed pesan...")
        result = stego.embed_message(audio_file, message, password, analyze_quality=True)
        print(f"✅ Pesan berhasil disimpan di: {result['output_file']}")
        
        if 'quality_metrics' in result:
            print(f"📊 PSNR: {result['quality_metrics']['psnr_db']} dB")
            print(f"📊 MSE: {result['quality_metrics']['mse']}")
            print(f"📊 SNR: {result['quality_metrics']['snr_db']} dB")
        
        # Test extract
        print(f"\n🔍 Testing extract pesan...")
        extracted_message = stego.extract_message(result['output_file'], password)
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