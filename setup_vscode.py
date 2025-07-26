"""
Script Setup untuk Visual Studio Code
=====================================

Script ini membantu setup proyek steganografi audio di VS Code.
Membuat konfigurasi yang diperlukan dan menguji dependencies.

Author: modo
Date: 2025
"""

import os
import json
import subprocess
import sys


def create_vscode_config():
    """
    Membuat konfigurasi VS Code untuk proyek
    """
    print("🔧 Membuat konfigurasi VS Code...")
    
    # Buat folder .vscode jika belum ada
    vscode_dir = '.vscode'
    if not os.path.exists(vscode_dir):
        os.makedirs(vscode_dir)
    
    # Konfigurasi launch.json untuk debugging
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Test Steganography",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "args": ["test"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "Embed Message",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "args": ["embed", "samples/test.wav", "Hello World!", "password123"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "Extract Message",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "args": ["extract", "output/test_stego.wav", "password123"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    
    with open(os.path.join(vscode_dir, 'launch.json'), 'w') as f:
        json.dump(launch_config, f, indent=4)
    
    # Konfigurasi settings.json
    settings_config = {
        "python.defaultInterpreterPath": "./steganografi_env/Scripts/python.exe",
        "python.terminal.activateEnvironment": True,
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.formatting.provider": "black",
        "files.associations": {
            "*.py": "python"
        },
        "python.testing.pytestEnabled": True,
        "python.testing.pytestArgs": [
            "tests"
        ]
    }
    
    with open(os.path.join(vscode_dir, 'settings.json'), 'w') as f:
        json.dump(settings_config, f, indent=4)
    
    # Konfigurasi tasks.json
    tasks_config = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Install Dependencies",
                "type": "shell",
                "command": "pip",
                "args": ["install", "-r", "requirements.txt"],
                "group": "build",
                "presentation": {
                    "reveal": "always",
                    "panel": "new"
                }
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "python",
                "args": ["main.py", "test"],
                "group": "test",
                "presentation": {
                    "reveal": "always",
                    "panel": "new"
                }
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "black",
                "args": [".", "--line-length", "100"],
                "group": "build",
                "presentation": {
                    "reveal": "silent"
                }
            }
        ]
    }
    
    with open(os.path.join(vscode_dir, 'tasks.json'), 'w') as f:
        json.dump(tasks_config, f, indent=4)
    
    print("✅ Konfigurasi VS Code berhasil dibuat!")


def check_python_version():
    """
    Cek versi Python
    """
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ diperlukan!")
        return False
    
    print("✅ Python version OK")
    return True


def install_dependencies():
    """
    Install dependencies yang diperlukan
    """
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip terlebih dahulu
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install dari requirements.txt
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies berhasil diinstall!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def test_imports():
    """
    Test apakah semua module bisa diimport
    """
    print("🧪 Testing imports...")
    
    modules_to_test = [
        'cryptography',
        'librosa', 
        'soundfile',
        'numpy',
        'pydub',
        'mutagen'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Gagal import: {', '.join(failed_imports)}")
        print("Coba install ulang dengan: pip install -r requirements.txt")
        return False
    
    print("✅ Semua imports berhasil!")
    return True


def create_sample_directories():
    """
    Buat direktori sample yang diperlukan
    """
    print("📁 Creating sample directories...")
    
    directories = [
        'samples',
        'output', 
        'temp',
        'tests'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✅ Created: {directory}/")
            
            # Buat .gitkeep untuk directory kosong
            gitkeep_file = os.path.join(directory, '.gitkeep')
            with open(gitkeep_file, 'w') as f:
                f.write('')
        else:
            print(f"  ℹ️  Already exists: {directory}/")


def create_sample_files():
    """
    Buat file sample untuk testing
    """
    print("📄 Creating sample files...")
    
    # Buat file .env sample
    env_sample = """# Environment Variables untuk Steganografi Audio

# Development Settings
DEBUG=True
LOG_LEVEL=INFO

# Default Settings
DEFAULT_SAMPLE_RATE=44100
DEFAULT_BIT_DEPTH=16

# Security Settings (Opsional)
# MIN_PASSWORD_LENGTH=6
# MAX_MESSAGE_LENGTH=10000
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_sample)
    print("  ✅ Created: .env.example")
    
    # Buat file .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
steganografi_env/
ENV/
env.bak/
venv.bak/

# VS Code
.vscode/
*.code-workspace

# Audio files
*.wav
*.mp3
*.flac
*.ogg
*.aac

# Output files
output/
temp/
*.tmp

# OS
.DS_Store
Thumbs.db

# Environment variables
.env

# Logs
*.log

# Test outputs
test_*.wav
*_stego.*
*_backup.*
*_converted.*
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("  ✅ Created: .gitignore")


def show_setup_instructions():
    """
    Tampilkan instruksi setup
    """
    print("""
🎉 SETUP SELESAI!

LANGKAH SELANJUTNYA:
1. Buka VS Code di direktori ini
2. Install Python Extension jika belum ada
3. Select Python Interpreter (Ctrl+Shift+P > "Python: Select Interpreter")
4. Pilih interpreter dari virtual environment jika ada

UNTUK MEMULAI DEVELOPMENT:
1. Letakkan file audio sample di folder 'samples/'
2. Jalankan test: python main.py test
3. Coba embed: python main.py embed samples/audio.wav "Hello World!" "password123"
4. Coba extract: python main.py extract output/audio_stego.wav "password123"

DEBUGGING DI VS CODE:
- Tekan F5 untuk menjalankan konfigurasi debug
- Pilih "Test Steganography" untuk testing otomatis
- Pilih "Embed Message" atau "Extract Message" untuk testing manual

STRUKTUR PROYEK:
- src/              : Module utama sistem
- samples/          : File audio untuk testing
- output/           : File hasil steganografi
- temp/             : File temporary
- main.py           : Script utama
- requirements.txt  : Dependencies
- .vscode/          : Konfigurasi VS Code

Happy Coding! 🚀
""")


def main():
    """
    Fungsi utama setup
    """
    print("=" * 60)
    print("🔧 SETUP SISTEM STEGANOGRAFI AUDIO")
    print("=" * 60)
    
    # Cek Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependencies gagal diinstall. Lanjutkan manual dengan:")
        print("pip install -r requirements.txt")
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Beberapa module gagal diimport. Setup mungkin belum selesai.")
    
    # Buat konfigurasi
    create_vscode_config()
    create_sample_directories()
    create_sample_files()
    
    # Tampilkan instruksi
    show_setup_instructions()
    
    print("✅ Setup selesai! Siap untuk development.")


if __name__ == "__main__":
    main()