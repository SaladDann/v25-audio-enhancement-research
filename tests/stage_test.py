"""
Prueba de etapa (Stage Test) para V25.
Compara la representación de picos (coeficientes) con la señal sintetizada final.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'v25')))

import numpy as np
import soundfile as sf
import static_ffmpeg
static_ffmpeg.add_paths()
from scipy.signal import stft

from config import CFG
from encoder import _decode_mp3_to_array
from id3_payload import extract
from sbr import _as_2d, _deserialize, decompress_residual

def main():
    print("--- PRUEBA DE ETAPA STFT ---\n")

    orig, sr = sf.read(CFG.original_wav)
    orig = _as_2d(orig)
    base, _ = _decode_mp3_to_array(CFG.base_mp3)
    base = _as_2d(base)
    n = min(len(orig), len(base))
    residual = orig[:n] - base[:n]

    meta = extract(CFG.base_mp3, CFG.tag_desc)
    d = _deserialize(meta["payload"])
    all_frames = d["all_frames"]

    frame_len = meta["frame_len"]
    hop = meta["hop"]
    bands = meta["bands"]

    # 1. STFT del original
    window = np.hanning(frame_len)
    f_ref, t_ref, Z_ref = stft(residual[:, 0], sr, window=window, nperseg=frame_len, noverlap=frame_len - hop)

    # 2. Reconstrucción de coeficientes (sin síntesis temporal)
    Z_rec = np.zeros_like(Z_ref)
    n_t = min(Z_ref.shape[1], len(all_frames[0]))
    freqs = np.fft.rfftfreq(frame_len, 1 / sr)

    for i in range(n_t):
        for (k, f6, m6, p6, maxq) in all_frames[0][i]:
            bw = bands[k + 1] - bands[k]
            f_hz = bands[k] + (f6 / 63.0) * bw
            mag = 10 ** ((maxq - 128) / 20.0)
            ph = (p6 / 63.0) * 2 * np.pi - np.pi
            bin_idx = int(np.argmin(np.abs(f_ref - f_hz)))
            if bin_idx < Z_rec.shape[0]:
                Z_rec[bin_idx, i] += mag * np.exp(1j * ph)

    # 3. STFT de la síntesis final
    res_syn = decompress_residual(meta, base, CFG)[:n, 0]
    f_syn, t_syn, Z_syn = stft(res_syn, sr, window=window, nperseg=frame_len, noverlap=frame_len - hop)

    # Comparaciones
    mask_freq = (f_ref >= 100) & (f_ref < 16000)
    Z_r = Z_ref[mask_freq, :n_t]
    Z_q = Z_rec[mask_freq, :n_t]
    Z_s = Z_syn[mask_freq, :n_t]

    # Correlación de magnitudes en los picos
    peak_mask = np.abs(Z_q) > 0
    corr_mag = float(np.corrcoef(np.abs(Z_r[peak_mask]), np.abs(Z_q[peak_mask]))[0, 1])

    # Correlación compleja en la síntesis final
    corr_syn = float(np.abs(np.sum(Z_r * np.conj(Z_s))) /
                     (np.sqrt(np.sum(np.abs(Z_r)**2) * np.sum(np.abs(Z_s)**2)) + 1e-12))

    corr_temporal = float(np.corrcoef(residual[:n, 0], res_syn)[0, 1])

    print("--- Resultados ---")
    print(f"  Correlación de magnitud (Picos vs STFT Real): {corr_mag:+.4f}")
    print(f"  Correlación compleja (Síntesis vs STFT Real): {corr_syn:+.4f}")
    print(f"  Correlación temporal (Tiempo): {corr_temporal:+.4f}")
    print("\n  (La correlación de magnitud mide la calidad de la representación)")
    print("  (La correlación compleja mide la calidad de la síntesis)")

if __name__ == "__main__":
    main()
