"""
Script de diagnóstico detallado para V25.
Audita el payload extraído del MP3 y verifica la ganancia óptima que debería aplicarse.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'v25')))

import numpy as np
import soundfile as sf
import static_ffmpeg
static_ffmpeg.add_paths()

from config import CFG
from encoder import _decode_mp3_to_array
from id3_payload import extract
from sbr import decompress_residual, _as_2d

def main():
    print(f"--- DIAGNÓSTICO PARA: {CFG.tag_desc} ---\n")

    meta = extract(CFG.base_mp3, CFG.tag_desc)
    if meta is None:
        print(f"Error: No se encontró el tag.")
        return

    print(f"Tamaño del payload: {len(meta['payload'])} bytes")
    print(f"Ganancia de calibración: {meta.get('calibration_gain', 1.0):.6f}")
    print(f"Ganancias por canal: {meta.get('per_channel_gains', [])}\n")

    orig, sr = sf.read(CFG.original_wav)
    orig = _as_2d(orig)
    base, _ = _decode_mp3_to_array(CFG.base_mp3)
    n = min(len(orig), len(base))
    orig, base = orig[:n], base[:n]
    res_real = orig - base

    res_rec = decompress_residual(meta, base, CFG)
    res_rec = _as_2d(res_rec)[:n]

    print("--- Energía (RMS) ---")
    for c in range(min(2, res_real.shape[1])):
        rms_real = np.sqrt(np.mean(res_real[:, c] ** 2))
        rms_rec = np.sqrt(np.mean(res_rec[:, c] ** 2))
        ratio = rms_rec / (rms_real + 1e-12)
        corr = float(np.corrcoef(res_real[:, c], res_rec[:, c])[0, 1])
        print(f"  Canal {c}: RMS real={rms_real:.6f} | RMS rec={rms_rec:.6f} | Ratio={ratio:.4f} | Corr={corr:+.4f}")

    print("\n--- Ganancia Óptima Teórica (Diagnóstico) ---")
    for c in range(min(2, res_real.shape[1])):
        r = res_real[:, c]
        q = res_rec[:, c]
        a_star = float(np.sum(r * q) / (np.sum(q ** 2) + 1e-12))
        print(f"  Canal {c}: a* calculado = {a_star:+.4f}")

    print("\n--- Comparativa de SNR ---")
    for c in range(min(2, res_real.shape[1])):
        o = orig[:, c]
        b = base[:, c]
        e = np.clip(b + res_rec[:, c], -1, 1)

        snr_b = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - b) ** 2) + 1e-12))
        snr_e = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - e) ** 2) + 1e-12))
        print(f"  Canal {c}: Base={snr_b:.4f} dB | V25={snr_e:.4f} dB | Mejora={snr_e - snr_b:+.4f} dB")

if __name__ == "__main__":
    main()
