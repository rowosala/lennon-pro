"""
Script Utama - Sistem Steganografi Audio dengan Enkripsi AES-128
================================================================

Script ini adalah interface utama untuk sistem steganografi audio.
Mendukung embedding dan extraction pesan tersembunyi dari file audio
dengan fitur analisis kualitas dan pengujian ketahanan.

Usage:
    python main.py embed <audio_file> <message> <password> [options]
    python main.py extract <stego_file> <password>
    python main.py info <audio_file>
    python main.py test
    python main.py robustness <stego_file> <password> <original_message>
    python main.py quality <original_file> <stego_file>

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
    
    def embed_message(self, audio_file: str, message: str, password: str, 
                     output_file: str = None, output_format: str = 'wav',
                     analyze_quality: bool = True):
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
                output_file = os.path.join('output', f"{os.path.splitext(os.path.basename(audio_file))[0]}_stego.{output_format}")
            
            result = self.stego.embed_message(audio_file, message, password, output_file, 
                                            output_format, analyze_quality)
            
            print("\n" + "=" * 60)
            print("✅ EMBEDDING BERHASIL!")
            print("=" * 60)
            print(f"📁 File input: {audio_file}")
            print(f"📝 Panjang pesan: {len(message)} karakter")
            print(f"💾 File output: {result['output_file']}")
            print(f"📊 Format output: {result['format']}")
            print(f"📊 Kapasitas terpakai: {len(message)}/{capacity['max_chars']} karakter ({result['capacity_used']:.1f}%)")
            
            if 'quality_metrics' in result:
                print("\n=== Analisis Kualitas Audio ===")
                metrics = result['quality_metrics']
                print(f"📊 PSNR: {metrics['psnr_db']} dB")
                print(f"📊 MSE: {metrics['mse']}")
                print(f"📊 SNR: {metrics['snr_db']} dB")
                
                # Interpretasi kualitas
                psnr = metrics['psnr_db']
                if psnr > 40:
                    quality = "Sangat Baik (hampir tidak terdeteksi)"
                elif psnr > 30:
                    quality = "Baik (perbedaan minimal)"
                elif psnr > 20:
                    quality = "Cukup (perbedaan terdengar sedikit)"
                else:
                    quality = "Kurang (perbedaan cukup terdengar)"
                
                print(f"🎵 Kualitas Audio: {quality}")
                print("=" * 30)
            
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
    
    def test_robustness(self, stego_file: str, password: str, original_message: str):
        """
        Menguji ketahanan steganografi terhadap berbagai serangan
        """
        try:
            print("=" * 60)
            print("🛡️  PENGUJIAN KETAHANAN STEGANOGRAFI")
            print("=" * 60)
            
            if not os.path.exists(stego_file):
                raise Exception(f"File tidak ditemukan: {stego_file}")
            
            print("📖 Membaca file audio...")
            import soundfile as sf
            stego_audio, sample_rate = sf.read(stego_file)
            
            print("🧪 Menjalankan pengujian ketahanan...")
            results = self.stego.test_robustness(stego_audio, sample_rate, password, original_message)
            
            print("\n" + "=" * 60)
            print("📊 HASIL PENGUJIAN KETAHANAN")
            print("=" * 60)
            
            test_names = {
                'original': 'Audio Asli (Kontrol)',
                'noise_low': 'Noise Rendah (0.5%)',
                'noise_medium': 'Noise Sedang (1.0%)',
                'noise_high': 'Noise Tinggi (2.0%)',
                'compression_light': 'Kompresi Ringan (20%)',
                'compression_heavy': 'Kompresi Berat (50%)'
            }
            
            passed_tests = 0
            total_tests = len(results)
            
            for test_key, test_name in test_names.items():
                result = results[test_key]
                status = "✅ PASSED" if result['success'] else "❌ FAILED"
                
                print(f"{test_name:<25} : {status}")
                
                if result['success']:
                    passed_tests += 1
                elif result['error']:
                    print(f"                          Error: {result['error']}")
                else:
                    print(f"                          Pesan tidak cocok")
            
            print("\n" + "-" * 60)
            print(f"📊 Ringkasan: {passed_tests}/{total_tests} test berhasil ({passed_tests/total_tests*100:.1f}%)")
            
            # Interpretasi hasil
            if passed_tests == total_tests:
                robustness = "Sangat Tahan (Excellent)"
            elif passed_tests >= total_tests * 0.8:
                robustness = "Tahan (Good)"
            elif passed_tests >= total_tests * 0.5:
                robustness = "Cukup Tahan (Fair)"
            else:
                robustness = "Kurang Tahan (Poor)"
            
            print(f"🛡️  Tingkat Ketahanan: {robustness}")
            print("-" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            sys.exit(1)
    
    def compare_quality(self, original_file: str, stego_file: str):
        """
        Membandingkan kualitas audio asli dengan stego audio
        """
        try:
            print("=" * 60)
            print("📊 ANALISIS KUALITAS AUDIO")
            print("=" * 60)
            
            if not os.path.exists(original_file):
                raise Exception(f"File asli tidak ditemukan: {original_file}")
            
            if not os.path.exists(stego_file):
                raise Exception(f"File stego tidak ditemukan: {stego_file}")
            
            print("📖 Membaca file audio...")
            import soundfile as sf
            
            original_audio, sr1 = sf.read(original_file)
            stego_audio, sr2 = sf.read(stego_file)
            
            if sr1 != sr2:
                print("⚠️  Warning: Sample rate berbeda antara kedua file")
            
            # Hitung metrik kualitas
            print("🔢 Menghitung metrik kualitas...")
            psnr = self.stego.calculate_psnr(original_audio, stego_audio)
            mse = self.stego.calculate_mse(original_audio, stego_audio)
            snr = self.stego.calculate_snr(original_audio, stego_audio)
            
            print("\n" + "=" * 60)
            print("📊 HASIL ANALISIS KUALITAS")
            print("=" * 60)
            print(f"📁 File asli: {original_file}")
            print(f"📁 File stego: {stego_file}")
            print(f"\n📊 PSNR: {psnr:.2f} dB")
            print(f"📊 MSE: {mse:.8f}")
            print(f"📊 SNR: {snr:.2f} dB")
            
            # Interpretasi kualitas
            if psnr > 40:
                quality = "Sangat Baik (hampir tidak terdeteksi)"
                emoji = "🟢"
            elif psnr > 30:
                quality = "Baik (perbedaan minimal)"
                emoji = "🟡"
            elif psnr > 20:
                quality = "Cukup (perbedaan terdengar sedikit)"
                emoji = "🟠"
            else:
                quality = "Kurang (perbedaan cukup terdengar)"
                emoji = "🔴"
            
            print(f"\n{emoji} Kualitas Audio: {quality}")
            
            # Rekomendasi
            print("\n=== Rekomendasi ===")
            if psnr > 30:
                print("✅ Kualitas sangat baik untuk steganografi")
                print("✅ Pesan tersembunyi sulit terdeteksi")
            elif psnr > 20:
                print("⚠️  Kualitas cukup, namun masih dapat diterima")
                print("⚠️  Pertimbangkan mengurangi panjang pesan")
            else:
                print("❌ Kualitas kurang baik")
                print("❌ Pertimbangkan menggunakan file audio yang lebih besar")
            
            print("=" * 20)
            
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
            
            # Test embedding dengan analisis kualitas
            print("\n📥 Testing embedding dengan analisis kualitas...")
            result = self.stego.embed_message(test_file, test_message, test_password, 
                                            analyze_quality=True)
            print(f"✓ Embedding berhasil: {result['output_file']}")
            
            if 'quality_metrics' in result:
                metrics = result['quality_metrics']
                print(f"✓ PSNR: {metrics['psnr_db']} dB")
                print(f"✓ MSE: {metrics['mse']}")
                print(f"✓ SNR: {metrics['snr_db']} dB")
            
            # Test extraction
            print("\n📤 Testing extraction...")
            extracted = self.stego.extract_message(result['output_file'], test_password)
            print(f"✓ Extraction berhasil: {len(extracted)} karakter")
            
            # Test pengujian ketahanan
            print("\n🛡️  Testing ketahanan...")
            stego_audio, sr = sf.read(result['output_file'])
            robustness_results = self.stego.test_robustness(stego_audio, sr, test_password, test_message)
            
            passed_robustness = sum(1 for r in robustness_results.values() if r['success'])
            total_robustness = len(robustness_results)
            
            print(f"✓ Ketahanan: {passed_robustness}/{total_robustness} test berhasil")
            
            # Verifikasi
            print("\n🔍 Verifikasi...")
            print(f"Original : {test_message}")
            print(f"Extracted: {extracted}")
            
            if test_message == extracted:
                print("\n🎉 ✅ SEMUA TEST PASSED! Sistem bekerja dengan baik.")
                print(f"📊 Kualitas PSNR: {metrics['psnr_db'] if 'quality_metrics' in result else 'N/A'} dB")
                print(f"🛡️  Ketahanan: {passed_robustness}/{total_robustness} test")
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
    python main.py embed <audio_file> <message> <password> [options]
    python main.py extract <stego_file> <password>
    python main.py info <audio_file>
    python main.py test
    python main.py robustness <stego_file> <password> <original_message>
    python main.py quality <original_file> <stego_file>

PERINTAH:
    embed      - Sisipkan pesan terenkripsi ke file audio
    extract    - Ekstrak dan dekripsi pesan dari file audio
    info       - Tampilkan informasi file audio
    test       - Jalankan test otomatis sistem
    robustness - Uji ketahanan steganografi terhadap serangan
    quality    - Analisis kualitas perbandingan audio

OPTIONS untuk embed:
    --format FORMAT    : Format output (wav, flac, mp3) [default: wav]
    --output FILE      : File output custom
    --no-analysis      : Skip analisis kualitas

CONTOH:
    python main.py embed "music.wav" "Pesan rahasia" "password123"
    python main.py embed "music.wav" "Pesan" "pass123" --format flac
    python main.py extract "music_stego.wav" "password123"
    python main.py info "music.wav"
    python main.py robustness "music_stego.wav" "password123" "Pesan rahasia"
    python main.py quality "music.wav" "music_stego.wav"
    python main.py test

FITUR BARU:
    ✨ Analisis kualitas audio (PSNR, MSE, SNR)
    ✨ Pengujian ketahanan terhadap noise dan kompresi
    ✨ Dukungan format output: WAV, FLAC, MP3
    ✨ Perbandingan kualitas audio asli vs stego

CATATAN:
    - Mendukung format input: WAV, MP3, FLAC
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
                print("❌ Format: python main.py embed <audio_file> <message> <password> [options]")
                sys.exit(1)
            
            audio_file = sys.argv[2]
            message = sys.argv[3]
            password = sys.argv[4]
            
            # Parse options
            output_file = None
            output_format = 'wav'
            analyze_quality = True
            
            i = 5
            while i < len(sys.argv):
                if sys.argv[i] == '--format' and i + 1 < len(sys.argv):
                    output_format = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--no-analysis':
                    analyze_quality = False
                    i += 1
                else:
                    i += 1
            
            app.embed_message(audio_file, message, password, output_file, output_format, analyze_quality)
            
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
            
        elif command == 'robustness':
            if len(sys.argv) < 5:
                print("❌ Format: python main.py robustness <stego_file> <password> <original_message>")
                sys.exit(1)
            
            stego_file = sys.argv[2]
            password = sys.argv[3]
            original_message = sys.argv[4]
            
            app.test_robustness(stego_file, password, original_message)
            
        elif command == 'quality':
            if len(sys.argv) < 4:
                print("❌ Format: python main.py quality <original_file> <stego_file>")
                sys.exit(1)
            
            original_file = sys.argv[2]
            stego_file = sys.argv[3]
            
            app.compare_quality(original_file, stego_file)
            
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