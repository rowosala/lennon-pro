"""
Module Quality Analyzer
=======================

Module ini berisi fungsi-fungsi untuk menganalisis kualitas audio
dan melakukan pengujian ketahanan steganografi.

Author: modo
Date: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import signal
from typing import Dict, List, Tuple
import os


class QualityAnalyzer:
    """
    Kelas untuk analisis kualitas audio dan pengujian ketahanan
    """
    
    def __init__(self):
        pass
    
    def calculate_spectral_distortion(self, original: np.ndarray, modified: np.ndarray, 
                                    sample_rate: int = 44100) -> Dict:
        """
        Menghitung distorsi spektral antara audio asli dan termodifikasi
        
        Args:
            original (np.ndarray): Audio asli
            modified (np.ndarray): Audio termodifikasi
            sample_rate (int): Sample rate audio
            
        Returns:
            Dict: Metrik distorsi spektral
        """
        # Pastikan kedua array memiliki panjang yang sama
        min_len = min(len(original), len(modified))
        original = original[:min_len]
        modified = modified[:min_len]
        
        # Hitung FFT untuk kedua sinyal
        fft_original = np.fft.fft(original)
        fft_modified = np.fft.fft(modified)
        
        # Hitung magnitude spectrum
        mag_original = np.abs(fft_original)
        mag_modified = np.abs(fft_modified)
        
        # Hitung Spectral Distortion
        spectral_diff = mag_original - mag_modified
        spectral_distortion = np.mean(np.abs(spectral_diff))
        
        # Hitung Spectral Correlation
        correlation = np.corrcoef(mag_original, mag_modified)[0, 1]
        
        # Hitung Spectral Centroid difference
        freqs = np.fft.fftfreq(len(original), 1/sample_rate)
        centroid_original = np.sum(freqs[:len(freqs)//2] * mag_original[:len(freqs)//2]) / np.sum(mag_original[:len(freqs)//2])
        centroid_modified = np.sum(freqs[:len(freqs)//2] * mag_modified[:len(freqs)//2]) / np.sum(mag_modified[:len(freqs)//2])
        centroid_diff = abs(centroid_original - centroid_modified)
        
        return {
            'spectral_distortion': spectral_distortion,
            'spectral_correlation': correlation,
            'centroid_difference': centroid_diff,
            'centroid_original': centroid_original,
            'centroid_modified': centroid_modified
        }
    
    def calculate_thd(self, audio: np.ndarray, sample_rate: int = 44100, 
                     fundamental_freq: float = 440.0) -> float:
        """
        Menghitung Total Harmonic Distortion (THD)
        
        Args:
            audio (np.ndarray): Data audio
            sample_rate (int): Sample rate
            fundamental_freq (float): Frekuensi fundamental
            
        Returns:
            float: Nilai THD dalam persen
        """
        # Hitung FFT
        fft_data = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
        magnitude = np.abs(fft_data)
        
        # Cari indeks frekuensi fundamental
        fundamental_idx = np.argmin(np.abs(freqs - fundamental_freq))
        fundamental_power = magnitude[fundamental_idx] ** 2
        
        # Cari harmonik (2f, 3f, 4f, 5f)
        harmonic_power = 0
        for harmonic in range(2, 6):  # 2nd to 5th harmonic
            harmonic_freq = fundamental_freq * harmonic
            if harmonic_freq < sample_rate / 2:  # Nyquist limit
                harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
                harmonic_power += magnitude[harmonic_idx] ** 2
        
        # Hitung THD
        if fundamental_power > 0:
            thd = np.sqrt(harmonic_power / fundamental_power) * 100
        else:
            thd = 0
        
        return thd
    
    def generate_quality_report(self, original_file: str, stego_file: str, 
                              output_dir: str = 'output') -> str:
        """
        Generate laporan kualitas lengkap
        
        Args:
            original_file (str): Path file audio asli
            stego_file (str): Path file stego audio
            output_dir (str): Direktori output laporan
            
        Returns:
            str: Path file laporan
        """
        # Baca file audio
        original_audio, sr1 = sf.read(original_file)
        stego_audio, sr2 = sf.read(stego_file)
        
        if sr1 != sr2:
            raise Exception("Sample rate berbeda antara kedua file")
        
        sample_rate = sr1
        
        # Hitung berbagai metrik
        from .audio_steganografi import AudioSteganography
        stego = AudioSteganography()
        
        psnr = stego.calculate_psnr(original_audio, stego_audio)
        mse = stego.calculate_mse(original_audio, stego_audio)
        snr = stego.calculate_snr(original_audio, stego_audio)
        
        spectral_metrics = self.calculate_spectral_distortion(original_audio, stego_audio, sample_rate)
        thd_original = self.calculate_thd(original_audio, sample_rate)
        thd_stego = self.calculate_thd(stego_audio, sample_rate)
        
        # Generate laporan
        report_content = f"""
LAPORAN ANALISIS KUALITAS AUDIO STEGANOGRAFI
============================================

File Asli: {original_file}
File Stego: {stego_file}
Tanggal Analisis: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

METRIK KUALITAS DASAR
---------------------
PSNR (Peak Signal-to-Noise Ratio): {psnr:.2f} dB
MSE (Mean Squared Error): {mse:.8f}
SNR (Signal-to-Noise Ratio): {snr:.2f} dB

ANALISIS SPEKTRAL
-----------------
Distorsi Spektral: {spectral_metrics['spectral_distortion']:.6f}
Korelasi Spektral: {spectral_metrics['spectral_correlation']:.4f}
Perbedaan Centroid: {spectral_metrics['centroid_difference']:.2f} Hz
Centroid Asli: {spectral_metrics['centroid_original']:.2f} Hz
Centroid Stego: {spectral_metrics['centroid_modified']:.2f} Hz

ANALISIS HARMONIK
-----------------
THD Audio Asli: {thd_original:.4f}%
THD Audio Stego: {thd_stego:.4f}%
Perubahan THD: {abs(thd_stego - thd_original):.4f}%

INTERPRETASI KUALITAS
--------------------
"""
        
        # Interpretasi PSNR
        if psnr > 40:
            report_content += "PSNR: Sangat Baik (>40 dB) - Hampir tidak terdeteksi\n"
        elif psnr > 30:
            report_content += "PSNR: Baik (30-40 dB) - Perbedaan minimal\n"
        elif psnr > 20:
            report_content += "PSNR: Cukup (20-30 dB) - Perbedaan terdengar sedikit\n"
        else:
            report_content += "PSNR: Kurang (<20 dB) - Perbedaan cukup terdengar\n"
        
        # Interpretasi korelasi spektral
        if spectral_metrics['spectral_correlation'] > 0.99:
            report_content += "Korelasi Spektral: Sangat Tinggi (>0.99) - Spektrum hampir identik\n"
        elif spectral_metrics['spectral_correlation'] > 0.95:
            report_content += "Korelasi Spektral: Tinggi (0.95-0.99) - Spektrum sangat mirip\n"
        elif spectral_metrics['spectral_correlation'] > 0.90:
            report_content += "Korelasi Spektral: Sedang (0.90-0.95) - Spektrum cukup mirip\n"
        else:
            report_content += "Korelasi Spektral: Rendah (<0.90) - Spektrum berbeda signifikan\n"
        
        report_content += f"""
REKOMENDASI
-----------
"""
        
        if psnr > 30 and spectral_metrics['spectral_correlation'] > 0.95:
            report_content += "✅ Kualitas steganografi sangat baik\n"
            report_content += "✅ Pesan tersembunyi sulit terdeteksi\n"
            report_content += "✅ Dapat digunakan untuk aplikasi sensitif\n"
        elif psnr > 20 and spectral_metrics['spectral_correlation'] > 0.90:
            report_content += "⚠️  Kualitas steganografi cukup baik\n"
            report_content += "⚠️  Pertimbangkan mengurangi panjang pesan\n"
            report_content += "⚠️  Cocok untuk aplikasi umum\n"
        else:
            report_content += "❌ Kualitas steganografi kurang optimal\n"
            report_content += "❌ Pertimbangkan menggunakan file audio yang lebih besar\n"
            report_content += "❌ Atau kurangi panjang pesan secara signifikan\n"
        
        # Simpan laporan
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, 'quality_report.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_file
    
    def plot_waveform_comparison(self, original_file: str, stego_file: str, 
                               output_dir: str = 'output') -> str:
        """
        Membuat plot perbandingan waveform
        
        Args:
            original_file (str): Path file audio asli
            stego_file (str): Path file stego audio
            output_dir (str): Direktori output plot
            
        Returns:
            str: Path file plot
        """
        # Baca file audio
        original_audio, sr1 = sf.read(original_file)
        stego_audio, sr2 = sf.read(stego_file)
        
        # Ambil sampel untuk plotting (maksimal 1 detik)
        max_samples = min(sr1, len(original_audio), len(stego_audio))
        original_sample = original_audio[:max_samples]
        stego_sample = stego_audio[:max_samples]
        
        # Buat time axis
        time = np.linspace(0, len(original_sample) / sr1, len(original_sample))
        
        # Create plot
        plt.figure(figsize=(12, 8))
        
        # Plot waveform asli
        plt.subplot(3, 1, 1)
        plt.plot(time, original_sample, 'b-', linewidth=0.5)
        plt.title('Audio Asli')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        # Plot waveform stego
        plt.subplot(3, 1, 2)
        plt.plot(time, stego_sample, 'r-', linewidth=0.5)
        plt.title('Audio Stego')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        # Plot perbedaan
        plt.subplot(3, 1, 3)
        difference = original_sample - stego_sample
        plt.plot(time, difference, 'g-', linewidth=0.5)
        plt.title('Perbedaan (Asli - Stego)')
        plt.xlabel('Waktu (detik)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Simpan plot
        os.makedirs(output_dir, exist_ok=True)
        plot_file = os.path.join(output_dir, 'waveform_comparison.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_file
    
    def plot_spectrum_comparison(self, original_file: str, stego_file: str, 
                               output_dir: str = 'output') -> str:
        """
        Membuat plot perbandingan spektrum frekuensi
        
        Args:
            original_file (str): Path file audio asli
            stego_file (str): Path file stego audio
            output_dir (str): Direktori output plot
            
        Returns:
            str: Path file plot
        """
        # Baca file audio
        original_audio, sr1 = sf.read(original_file)
        stego_audio, sr2 = sf.read(stego_file)
        
        # Ambil sampel untuk analisis spektrum
        max_samples = min(8192, len(original_audio), len(stego_audio))  # 8192 samples untuk FFT
        original_sample = original_audio[:max_samples]
        stego_sample = stego_audio[:max_samples]
        
        # Hitung FFT
        fft_original = np.fft.fft(original_sample)
        fft_stego = np.fft.fft(stego_sample)
        
        # Hitung magnitude spectrum
        mag_original = np.abs(fft_original[:max_samples//2])
        mag_stego = np.abs(fft_stego[:max_samples//2])
        
        # Buat frequency axis
        freqs = np.fft.fftfreq(max_samples, 1/sr1)[:max_samples//2]
        
        # Create plot
        plt.figure(figsize=(12, 8))
        
        # Plot spektrum asli
        plt.subplot(2, 1, 1)
        plt.semilogy(freqs, mag_original, 'b-', linewidth=1, label='Audio Asli')
        plt.semilogy(freqs, mag_stego, 'r--', linewidth=1, alpha=0.7, label='Audio Stego')
        plt.title('Perbandingan Spektrum Frekuensi')
        plt.xlabel('Frekuensi (Hz)')
        plt.ylabel('Magnitude (log scale)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(0, sr1//2)
        
        # Plot perbedaan spektrum
        plt.subplot(2, 1, 2)
        diff_spectrum = mag_original - mag_stego
        plt.plot(freqs, diff_spectrum, 'g-', linewidth=1)
        plt.title('Perbedaan Spektrum (Asli - Stego)')
        plt.xlabel('Frekuensi (Hz)')
        plt.ylabel('Magnitude Difference')
        plt.grid(True, alpha=0.3)
        plt.xlim(0, sr1//2)
        
        plt.tight_layout()
        
        # Simpan plot
        os.makedirs(output_dir, exist_ok=True)
        plot_file = os.path.join(output_dir, 'spectrum_comparison.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_file


def test_quality_analyzer():
    """
    Test function untuk quality analyzer
    """
    print("=== Testing Quality Analyzer ===")
    
    analyzer = QualityAnalyzer()
    
    # Generate test audio
    import numpy as np
    import soundfile as sf
    
    duration = 1.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Audio asli (sinewave)
    original = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Audio dengan sedikit noise (simulasi stego)
    stego = original + 0.001 * np.random.randn(len(original))
    
    # Simpan file test
    os.makedirs('temp', exist_ok=True)
    original_file = 'temp/test_original.wav'
    stego_file = 'temp/test_stego.wav'
    
    sf.write(original_file, original, sample_rate)
    sf.write(stego_file, stego, sample_rate)
    
    try:
        # Test spectral analysis
        spectral_metrics = analyzer.calculate_spectral_distortion(original, stego, sample_rate)
        print(f"✓ Spectral distortion: {spectral_metrics['spectral_distortion']:.6f}")
        print(f"✓ Spectral correlation: {spectral_metrics['spectral_correlation']:.4f}")
        
        # Test THD calculation
        thd_original = analyzer.calculate_thd(original, sample_rate)
        thd_stego = analyzer.calculate_thd(stego, sample_rate)
        print(f"✓ THD original: {thd_original:.4f}%")
        print(f"✓ THD stego: {thd_stego:.4f}%")
        
        # Test report generation
        report_file = analyzer.generate_quality_report(original_file, stego_file)
        print(f"✓ Quality report generated: {report_file}")
        
        print("✅ Quality Analyzer test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")


if __name__ == "__main__":
    test_quality_analyzer()