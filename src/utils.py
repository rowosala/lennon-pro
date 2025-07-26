"""
Module Utilities
================

Module ini berisi fungsi-fungsi bantuan untuk sistem steganografi audio.

Author: modo
Date: 2025
"""

import os
import wave
import numpy as np
from pydub import AudioSegment
import soundfile as sf


def convert_to_wav(input_file: str, output_file: str = None) -> str:
    """
    Konversi file audio (MP3, FLAC, dll) ke format WAV
    
    Args:
        input_file (str): Path file audio input
        output_file (str, optional): Path output file WAV
        
    Returns:
        str: Path file WAV hasil konversi
        
    Penjelasan:
        - Mendukung konversi dari MP3, FLAC, dan format lainnya
        - Menggunakan pydub untuk handling berbagai format
        - Output dalam format WAV 16-bit untuk kompatibilitas LSB
    """
    try:
        if output_file is None:
            # Generate nama file output
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_converted.wav"
        
        # Load audio file dengan pydub
        audio = AudioSegment.from_file(input_file)
        
        # Convert ke WAV dengan parameter standar
        audio.export(
            output_file,
            format="wav",
            parameters=["-acodec", "pcm_s16le"]  # 16-bit PCM
        )
        
        print(f"✓ File berhasil dikonversi ke: {output_file}")
        return output_file
        
    except Exception as e:
        raise Exception(f"Error konversi file: {str(e)}")


def get_file_info(file_path: str) -> dict:
    """
    Mendapatkan informasi detail file audio
    
    Args:
        file_path (str): Path file audio
        
    Returns:
        dict: Informasi file audio
        
    Penjelasan:
        - Menggunakan soundfile untuk membaca metadata
        - Memberikan informasi sample rate, channels, duration, dll
        - Berguna untuk validasi file sebelum processing
    """
    try:
        # Baca informasi file
        data, samplerate = sf.read(file_path)
        
        info = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'sample_rate': samplerate,
            'channels': len(data.shape) if len(data.shape) > 1 else 1,
            'samples': len(data),
            'duration': len(data) / samplerate,
            'format': file_path.split('.')[-1].upper(),
            'max_message_size': len(data) // 8  # Estimasi maksimal bytes yang bisa disimpan
        }
        
        if len(data.shape) > 1:
            info['channels'] = data.shape[1]
            info['samples'] = data.shape[0]
            info['max_message_size'] = (data.shape[0] * data.shape[1]) // 8
        
        return info
        
    except Exception as e:
        raise Exception(f"Error membaca info file: {str(e)}")


def print_file_info(file_path: str):
    """
    Print informasi file audio dalam format yang readable
    
    Args:
        file_path (str): Path file audio
    """
    try:
        info = get_file_info(file_path)
        
        print("\n=== Informasi File Audio ===")
        print(f"File: {info['file_path']}")
        print(f"Format: {info['format']}")
        print(f"Ukuran File: {info['file_size']:,} bytes")
        print(f"Sample Rate: {info['sample_rate']:,} Hz")
        print(f"Channels: {info['channels']}")
        print(f"Total Samples: {info['samples']:,}")
        print(f"Duration: {info['duration']:.2f} seconds")
        print(f"Kapasitas Maksimal Pesan: ~{info['max_message_size']:,} bytes")
        print("=" * 30)
        
    except Exception as e:
        print(f"Error menampilkan info file: {str(e)}")


def validate_file(file_path: str) -> bool:
    """
    Validasi apakah file audio valid dan bisa diproses
    
    Args:
        file_path (str): Path file yang akan divalidasi
        
    Returns:
        bool: True jika file valid, False jika tidak
    """
    try:
        # Cek apakah file ada
        if not os.path.exists(file_path):
            print(f"✗ File tidak ditemukan: {file_path}")
            return False
        
        # Cek apakah file bisa dibaca sebagai audio
        data, samplerate = sf.read(file_path)
        
        # Cek apakah file memiliki data
        if len(data) == 0:
            print(f"✗ File audio kosong: {file_path}")
            return False
        
        # Cek apakah file cukup besar untuk menyimpan pesan
        min_samples = 100  # Minimal samples yang diperlukan
        if len(data) < min_samples:
            print(f"✗ File terlalu kecil untuk steganografi: {file_path}")
            return False
        
        print(f"✓ File valid dan siap diproses: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ File tidak valid: {str(e)}")
        return False


def create_backup(file_path: str) -> str:
    """
    Membuat backup file sebelum dimodifikasi
    
    Args:
        file_path (str): Path file yang akan di-backup
        
    Returns:
        str: Path file backup
    """
    try:
        # Generate nama file backup
        base_name = os.path.splitext(file_path)[0]
        extension = os.path.splitext(file_path)[1]
        backup_path = f"{base_name}_backup{extension}"
        
        # Copy file
        import shutil
        shutil.copy2(file_path, backup_path)
        
        print(f"✓ Backup dibuat: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"✗ Gagal membuat backup: {str(e)}")
        return None


def clean_temp_files(directory: str):
    """
    Membersihkan file temporary yang dibuat selama proses
    
    Args:
        directory (str): Directory yang akan dibersihkan
    """
    try:
        temp_patterns = ['*_temp.wav', '*_converted.wav', '*_backup.*']
        import glob
        
        for pattern in temp_patterns:
            files = glob.glob(os.path.join(directory, pattern))
            for file in files:
                try:
                    os.remove(file)
                    print(f"✓ File temporary dihapus: {file}")
                except:
                    pass
                    
    except Exception as e:
        print(f"Warning: Tidak bisa membersihkan file temporary: {str(e)}")


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test dengan file yang ada (sesuaikan path)
    test_file = "test_audio.wav"  # Ganti dengan file audio yang ada
    
    if os.path.exists(test_file):
        print_file_info(test_file)
        validate_file(test_file)
    else:
        print("Untuk testing, letakkan file audio bernama 'test_audio.wav' di directory ini")