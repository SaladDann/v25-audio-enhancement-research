"""
Módulo de evaluación objetiva de calidad de audio.
"""
import numpy as np
import soundfile as sf

def _align(a, b):
    n = min(len(a), len(b))
    return a[:n], b[:n]

def snr_db(reference: np.ndarray, test: np.ndarray) -> float:
    """Calcula la Relación Señal-Ruido (SNR) en decibelios."""
    ref, tst = _align(reference, test)
    noise = ref - tst
    p_sig = np.mean(ref ** 2) + 1e-12
    p_noi = np.mean(noise ** 2) + 1e-12
    return float(10 * np.log10(p_sig / p_noi))

def spectral_distance(reference: np.ndarray, test: np.ndarray, sr: int, n_fft: int = 2048) -> float:
    """Calcula la distancia espectral media usando STFT y norma L2."""
    ref, tst = _align(reference, test)
    if ref.ndim > 1: ref = ref.mean(axis=1)
    if tst.ndim > 1: tst = tst.mean(axis=1)

    hop = n_fft // 2
    frames = max(1, (len(ref) - n_fft) // hop)
    dists = []

    for i in range(frames):
        s = i * hop
        R = np.abs(np.fft.rfft(ref[s:s + n_fft] * np.hanning(n_fft)))
        T = np.abs(np.fft.rfft(tst[s:s + n_fft] * np.hanning(n_fft)))
        R /= np.linalg.norm(R) + 1e-12
        T /= np.linalg.norm(T) + 1e-12
        dists.append(float(np.linalg.norm(R - T)))

    return float(np.mean(dists))

def report(original_wav: str, base_mp3: str, enhanced_wav: str, cfg) -> dict:
    """Genera un reporte comparativo entre el original, el base y el mejorado."""
    from encoder import _decode_mp3_to_array
    orig, sr = sf.read(original_wav)
    base, _ = _decode_mp3_to_array(base_mp3)
    enh, _ = sf.read(enhanced_wav)

    return {
        "SNR_base_dB": round(snr_db(orig, base), 2),
        "SNR_enhanced_dB": round(snr_db(orig, enh), 2),
        "SpecDist_base": round(spectral_distance(orig, base, sr), 4),
        "SpecDist_enhanced": round(spectral_distance(orig, enh, sr), 4),
    }
