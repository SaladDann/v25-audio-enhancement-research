"""
Verificación de alineación de señales para V25.
Comprueba sample rates, canales, longitudes, lags y normalización.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'v25')))

import numpy as np
import soundfile as sf
import static_ffmpeg
static_ffmpeg.add_paths()
from scipy.signal import correlate

from config import CFG
from encoder import _decode_mp3_to_array
from sbr import _as_2d

def main():
    print("--- VERIFICACIÓN DE ALINEACIÓN ---\n")

    orig, sr_orig = sf.read(CFG.original_wav)
    orig = _as_2d(orig)
    base, sr_base = _decode_mp3_to_array(CFG.base_mp3)
    base = _as_2d(base)

    print(f"1. Sample Rate: orig={sr_orig} | base={sr_base} | Coinciden: {sr_orig == sr_base}")
    print(f"2. Canales: orig={orig.shape[1]} | base={base.shape[1]} | Coinciden: {orig.shape[1] == base.shape[1]}")
    print(f"3. Longitud: orig={len(orig)} | base={len(base)} | Diferencia={len(orig) - len(base)} muestras")

    n = min(len(orig), len(base))
    a = orig[:n, 0]
    b = base[:n, 0]

    # Búsqueda de lag en los primeros 10 segundos
    seg_len = min(n, sr_orig * 10)
    corr = correlate(a[:seg_len], b[:seg_len], mode="full")
    lags = np.arange(-len(b[:seg_len]) + 1, len(a[:seg_len]))

    max_lag = int(sr_orig * 0.05) # +/- 50 ms
    mask = np.abs(lags) <= max_lag
    best_lag = lags[mask][np.argmax(np.abs(corr[mask]))]

    print(f"4. Desfase (Lag): {best_lag} muestras ({best_lag / sr_orig * 1000:.3f} ms)")

    print(f"\n5. Normalización:")
    print(f"   |orig| max={np.max(np.abs(orig)):.6f} | RMS={np.sqrt(np.mean(orig**2)):.6f}")
    print(f"   |base| max={np.max(np.abs(base)):.6f} | RMS={np.sqrt(np.mean(base**2)):.6f}")

    residual = orig[:n] - base[:n]
    print(f"\n6. Definición de Residual:")
    print(f"   RMS Residual = {np.sqrt(np.mean(residual**2)):.6f}")
    print(f"   SNR Base = {10 * np.log10(np.mean(orig[:n]**2) / np.mean(residual**2)):.4f} dB")

    print("\n7. Determinismo del Decodificador Base:")
    b1, _ = _decode_mp3_to_array(CFG.base_mp3)
    b2, _ = _decode_mp3_to_array(CFG.base_mp3)
    diff = float(np.max(np.abs(_as_2d(b1) - _as_2d(b2))))
    print(f"   Diferencia entre dos decodificaciones: {diff:.10f}")

if __name__ == "__main__":
    main()
