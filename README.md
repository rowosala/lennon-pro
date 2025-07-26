# Sistem Steganografi Audio dengan Enkripsi AES-128

## Deskripsi Proyek
Sistem ini mengimplementasikan teknik steganografi pada file audio (MP3, FLAC, WAV) dengan menggunakan metode Least Significant Bit (LSB) dan enkripsi Advanced Encryption Standard (AES-128) untuk keamanan pesan.

## Fitur Utama
- Enkripsi pesan teks menggunakan AES-128
- Steganografi pada file audio dengan metode LSB
- Support untuk format audio: MP3, FLAC, WAV
- Ekstraksi dan dekripsi pesan tersembunyi
- Interface command-line yang user-friendly

## Setup Proyek di Visual Studio Code

### 1. Persyaratan Sistem
- Python 3.8 atau lebih baru
- Visual Studio Code
- Extension Python untuk VS Code

### 2. Instalasi Dependencies
Buka terminal di VS Code (Ctrl+`) dan jalankan perintah berikut:

```bash
# Install virtual environment (opsional tapi direkomendasikan)
python -m venv steganografi_env

# Aktivasi virtual environment
# Windows:
steganografi_env\Scripts\activate
# Linux/Mac:
source steganografi_env/bin/activate

# Install library yang dibutuhkan
pip install cryptography librosa soundfile numpy pydub mutagen
```

### 3. Struktur Proyek
```
steganografi-audio/
│
├── src/
│   ├── audio_steganography.py    # Module utama steganografi
│   ├── encryption.py             # Module enkripsi AES
│   └── utils.py                  # Utility functions
│
├── samples/                      # Folder untuk file audio sample
├── output/                       # Folder untuk output file
├── main.py                       # Script utama
├── requirements.txt              # Daftar dependencies
└── README.md                     # Dokumentasi proyek
```

### 4. Konfigurasi VS Code
1. Install Python Extension
2. Pilih interpreter Python yang sesuai (Ctrl+Shift+P > "Python: Select Interpreter")
3. Pastikan virtual environment terdeteksi

## Cara Penggunaan
```bash
# Menyisipkan pesan
python main.py embed "audio_file.wav" "Pesan rahasia" "password123"

# Mengekstrak pesan
python main.py extract "audio_with_message.wav" "password123"
```

## Penjelasan Teknis
- **AES-128**: Menggunakan mode CBC dengan padding PKCS7
- **LSB Steganography**: Memodifikasi bit terakhir dari setiap sample audio
- **Format Support**: Conversion otomatis untuk MP3 dan FLAC ke WAV untuk processing