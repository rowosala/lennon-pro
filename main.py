"""
Script Utama - Sistem Steganografi Audio dengan Enkripsi AES-128
================================================================

Script ini adalah interface utama untuk sistem steganografi audio.
Mendukung embedding dan extraction pesan tersembunyi dari file audio.

Usage:
    python main.py embed <audio_file> <message> <password> [output_file]
    python main.py extract <stego_file> <password>
    python main.py info <audio_file>
    python main.py test

Author: modo
Date: 2025
"""

import sys
import os
import argparse
from src.audio_steganografi import AudioSteganography
from src.utils import print_file_info, validate_file


class SteganographyApp:
    """
    Aplikasi utama untuk steganografi audio
    """
    
    def __init__(self):
        self.stego = AudioSteganography()
        self.setup_directories()
    
    def setup_directories(self):
        """
        Setup direktori yang diperlukan
        """
        directories = ['samples', 'output', 'temp']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✓ Direktori {directory}/ dibuat")
    
    def embed_message(self, audio_file: str, message: str, password: str, output_file: str = None):
        """
        Embed pesan ke dalam file audio
        """
        try:
            print("=" * 60)
            print("🔐 EMBEDDING PESAN KE AUDIO")
            print("=" * 60)
            
            # Validasi input
            if not os.path.exists(audio_file):
                raise Exception(f"File tidak ditemukan: {audio_file}")
            
            if len(message.strip()) == 0:
                raise Exception("Pesan tidak boleh kosong")
            
            if len(password) < 6:
                print("⚠️  Warning: Password sebaiknya minimal 6 karakter untuk keamanan")
            
            # Cek kapasitas
            capacity = self.stego.get_capacity(audio_file)
            if len(message) > capacity['max_chars']:
                raise Exception(f"Pesan terlalu panjang! Maksimal {capacity['max_chars']} karakter, input {len(message)} karakter")
            
            # Proses embedding
            if output_file is None:
                output_file = os.path.join('output', f"{os.path.splitext(os.path.basename(audio_file))[0]}_stego.wav")
            
            result_file = self.stego.embed_message(audio_file, message, password, output_file)
            
            print("\n" + "=" * 60)
            print("✅ EMBEDDING BERHASIL!")
            print("=" * 60)
            print(f"📁 File input: {audio_file}")
            print(f"📝 Panjang pesan: {len(message)} karakter")
            print(f"💾 File output: {result_file}")
            print(f"📊 Kapasitas terpakai: {len(message)}/{capacity['max_chars']} karakter ({len(message)/capacity['max_chars']*100:.1f}%)")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            sys.exit(1)
    
    def extract_message(self, stego_file: str, password: str):
        """
        Extract pesan dari file audio
        """
        try:
            print("=" * 60)
            print("🔍 EXTRACTING PESAN DARI AUDIO")
            print("=" * 60)
            
            # Validasi input
            if not os.path.exists(stego_file):
                raise Exception(f"File tidak ditemukan: {stego_file}")
            
            # Proses extraction
            message = self.stego.extract_message(stego_file, password)
            
            print("\n" + "=" * 60)
            print("✅ EXTRACTION BERHASIL!")
            print("=" * 60)
            print(f"📁 File input: {stego_file}")
            print(f"📝 Panjang pesan: {len(message)} karakter")
            print("\n" + "-" * 60)
            print("📄 PESAN TERSEMBUNYI:")
            print("-" * 60)
            print(message)
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            sys.exit(1)
    
    def show_info(self, audio_file: str):
        """
        Tampilkan informasi file audio
        """
        try:
            print("=" * 60)
            print("📊 INFORMASI FILE AUDIO")
            print("=" * 60)
            
            if not os.path.exists(audio_file):
                raise Exception(f"File tidak ditemukan: {audio_file}")
            
            print_file_info(audio_file)
            
            # Informasi kapasitas steganografi
            capacity = self.stego.get_capacity(audio_file)
            print("\n=== Kapasitas Steganografi ===")
            print(f"Maksimal pesan: {capacity['max_chars']:,} karakter")
            print(f"Maksimal data: {capacity['max_bytes']:,} bytes")
            print(f"Total kapasitas: {capacity['total_capacity']:,} bytes")
            print(f"Overhead sistem: {capacity['overhead']} bytes")
            print("=" * 30)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            sys.exit(1)
    
    def run_test(self):
        """
        Jalankan test otomatis
        """
        print("=" * 60)
        print("🧪 TESTING SISTEM STEGANOGRAFI")
        print("=" * 60)
        
        # Test dengan audio dummy (generate sinewave)
        try:
            import numpy as np
            import soundfile as sf
            
            # Generate audio test 1 detik, 44.1kHz, sinewave 440Hz
            duration = 1.0
            sample_rate = 44100
            frequency = 440
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            test_file = os.path.join('temp', 'test_audio.wav')
            sf.write(test_file, audio, sample_rate)
            
            print(f"✓ Audio test dibuat: {test_file}")
            
            # Test data
            test_message = "Hello World! Ini adalah test pesan steganografi dengan AES-128. 🔐"
            test_password = "testpassword123"
            
            print(f"📝 Test message: {test_message}")
            print(f"🔑 Test password: {test_password}")
            
            # Test embedding
            print("\n📥 Testing embedding...")
            output_file = os.path.join('temp', 'test_stego.wav')
            result = self.stego.embed_message(test_file, test_message, test_password, output_file)
            print(f"✓ Embedding berhasil: {result}")
            
            # Test extraction
            print("\n📤 Testing extraction...")
            extracted = self.stego.extract_message(result, test_password)
            print(f"✓ Extraction berhasil: {len(extracted)} karakter")
            
            # Verifikasi
            print("\n🔍 Verifikasi...")
            print(f"Original : {test_message}")
            print(f"Extracted: {extracted}")
            
            if test_message == extracted:
                print("\n🎉 ✅ SEMUA TEST PASSED! Sistem bekerja dengan baik.")
            else:
                print("\n❌ TEST FAILED! Ada kesalahan dalam sistem.")
                
        except Exception as e:
            print(f"\n❌ Test error: {str(e)}")
    
    def print_usage(self):
        """
        Tampilkan petunjuk penggunaan
        """
        print("""
🎵 Sistem Steganografi Audio dengan Enkripsi AES-128 🎵

PENGGUNAAN:
    python main.py embed <audio_file> <message> <password> [output_file]
    python main.py extract <stego_file> <password>
    python main.py info <audio_file>
    python main.py test

PERINTAH:
    embed    - Sisipkan pesan terenkripsi ke file audio
    extract  - Ekstrak dan dekripsi pesan dari file audio
    info     - Tampilkan informasi file audio
    test     - Jalankan test otomatis sistem

CONTOH:
    python main.py embed "music.wav" "Pesan rahasia" "password123"
    python main.py extract "music_stego.wav" "password123"
    python main.py info "music.wav"
    python main.py test

CATATAN:
    - Mendukung format: WAV, MP3, FLAC
    - Enkripsi menggunakan AES-128 dengan mode CBC
    - Steganografi menggunakan metode LSB
    - Password minimal 6 karakter untuk keamanan
    - File output default disimpan di folder 'output/'

Untuk bantuan lebih lanjut, baca file README.md
        """)


def main():
    """
    Fungsi utama aplikasi
    """
    app = SteganographyApp()
    
    if len(sys.argv) < 2:
        app.print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'embed':
            if len(sys.argv) < 5:
                print("❌ Format: python main.py embed <audio_file> <message> <password> [output_file]")
                sys.exit(1)
            
            audio_file = sys.argv[2]
            message = sys.argv[3]
            password = sys.argv[4]
            output_file = sys.argv[5] if len(sys.argv) > 5 else None
            
            app.embed_message(audio_file, message, password, output_file)
            
        elif command == 'extract':
            if len(sys.argv) < 4:
                print("❌ Format: python main.py extract <stego_file> <password>")
                sys.exit(1)
            
            stego_file = sys.argv[2]
            password = sys.argv[3]
            
            app.extract_message(stego_file, password)
            
        elif command == 'info':
            if len(sys.argv) < 3:
                print("❌ Format: python main.py info <audio_file>")
                sys.exit(1)
            
            audio_file = sys.argv[2]
            app.show_info(audio_file)
            
        elif command == 'test':
            app.run_test()
            
        else:
            print(f"❌ Perintah tidak dikenal: {command}")
            app.print_usage()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Proses dibatalkan oleh user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error tidak terduga: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()