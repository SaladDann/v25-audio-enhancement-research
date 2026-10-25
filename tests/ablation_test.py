"""
Prueba de ablación para V25.
Reconstruye usando solo picos y compara el efecto de la calibración de ganancia.
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
from sbr import _as_2d, _deserialize, _synthesize

def main():
    print(f"--- PRUEBA DE ABLACIÓN: {CFG.tag_desc} ---\n")

    orig, sr = sf.read(CFG.original_wav)
    orig = _as_2d(orig)
    base, _ = _decode_mp3_to_array(CFG.base_mp3)
    base = _as_2d(base)
    n = min(len(orig), len(base))
    orig, base = orig[:n], base[:n]
    residual = orig - base

    meta = extract(CFG.base_mp3, CFG.tag_desc)
    if meta is None:
        print("Error: No se encontró el tag.")
        return

    d = _deserialize(meta["payload"])
    all_frames = d["all_frames"]
    bands = meta["bands"]
    frame_len = meta["frame_len"]
    hop = meta["hop"]
    n_samples = meta["n_samples"]
    channels = meta["channels"]
    calib = meta.get("calibration_gain", 1.0)

    # 1. Reconstrucción sin calibración
    print("--- 1. Picos SIN calibración (Ganancia = 1.0) ---")
    res_raw = _synthesize(all_frames, bands, frame_len, hop, sr, n_samples, channels, gain=1.0)

    for c in range(min(2, residual.shape[1])):
        r = residual[:, c]
        q = res_raw[:, c]
        b = base[:, c]
        o = orig[:, c]

        snr_b = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - b) ** 2) + 1e-12))
        snr_e = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - np.clip(b + q, -1, 1)) ** 2) + 1e-12))
        corr = float(np.corrcoef(r, q)[0, 1])
        a_star = float(np.sum(r * q) / (np.sum(q ** 2) + 1e-12))

        print(f"  Canal {c}: Corr={corr:+.4f} | Delta SNR={snr_e - snr_b:+.4f} dB | a* óptimo={a_star:+.4f}")

    # 2. Reconstrucción con calibración
    print(f"\n--- 2. Picos CON calibración (Ganancia = {calib:.4f}) ---")
    res_cal = _synthesize(all_frames, bands, frame_len, hop, sr, n_samples, channels, gain=calib)

    for c in range(min(2, residual.shape[1])):
        r = residual[:, c]
        q = res_cal[:, c]
        b = base[:, c]
        o = orig[:, c]

        snr_b = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - b) ** 2) + 1e-12))
        snr_e = 10 * np.log10((np.mean(o ** 2) + 1e-12) / (np.mean((o - np.clip(b + q, -1, 1)) ** 2) + 1e-12))
        corr = float(np.corrcoef(r, q)[0, 1])

        print(f"  Canal {c}: Corr={corr:+.4f} | Delta SNR={snr_e - snr_b:+.4f} dB")

if __name__ == "__main__":
    main()
