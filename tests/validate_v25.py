"""
Prueba de validación principal para V25.
Verifica la consistencia de las métricas de SNR, la reproducibilidad del decodificador
y la efectividad de la calibración de amplitud.
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

def snr_global(orig, test):
    """Calcula el SNR global basado en la energía total."""
    p_sig = float(np.sum(orig ** 2)) + 1e-12
    p_err = float(np.sum((orig - test) ** 2)) + 1e-12
    return 10 * np.log10(p_sig / p_err)

def snr_per_channel(orig, test):
    """Calcula el SNR por cada canal individual."""
    out = []
    for c in range(orig.shape[1]):
        p_sig = float(np.sum(orig[:, c] ** 2)) + 1e-12
        p_err = float(np.sum((orig[:, c] - test[:, c]) ** 2)) + 1e-12
        out.append(10 * np.log10(p_sig / p_err))
    return out

def main():
    print("--- VALIDACIÓN V25: CONSISTENCIA DE MÉTRICAS ---\n")

    orig, sr = sf.read(CFG.original_wav)
    orig = _as_2d(orig)
    base, _ = _decode_mp3_to_array(CFG.base_mp3)
    base = _as_2d(base)

    n = min(len(orig), len(base))
    orig = orig[:n]
    base = base[:n]

    meta = extract(CFG.base_mp3, CFG.tag_desc)
    if meta is None:
        print(f"Error: No se pudo extraer el tag {CFG.tag_desc}")
        return

    res_rec = decompress_residual(meta, base, CFG)
    res_rec = _as_2d(res_rec)[:n]

    # 1. SNR Base vs Enhanced
    snr_base_global = snr_global(orig, base)
    snr_base_ch = snr_per_channel(orig, base)

    enhanced = np.clip(base + res_rec, -1, 1)
    snr_enh_global = snr_global(orig, enhanced)
    snr_enh_ch = snr_per_channel(orig, enhanced)

    print("--- SNR Global ---")
    print(f"  Base: {snr_base_global:.4f} dB")
    print(f"  V25:  {snr_enh_global:.4f} dB (Delta: {snr_enh_global - snr_base_global:+.4f})")

    print("\n--- SNR por Canal ---")
    print(f"  Base Canal 0: {snr_base_ch[0]:.4f} dB | Canal 1: {snr_base_ch[1]:.4f} dB")
    print(f"  V25  Canal 0: {snr_enh_ch[0]:.4f} dB | Canal 1: {snr_enh_ch[1]:.4f} dB")

    # 2. Determinismo
    print("\n--- Determinismo del Decodificador ---")
    ress = [decompress_residual(meta, base, CFG) for _ in range(3)]
    diff_01 = float(np.max(np.abs(_as_2d(ress[0])[:n] - _as_2d(ress[1])[:n])))
    diff_12 = float(np.max(np.abs(_as_2d(ress[1])[:n] - _as_2d(ress[2])[:n])))
    print(f"  Diferencia max (Run 1 vs 2): {diff_01:.10f}")
    print(f"  Diferencia max (Run 2 vs 3): {diff_12:.10f}")
    if diff_01 == 0.0 and diff_12 == 0.0:
        print("  [OK] El decodificador es determinista.")
    else:
        print("  [ALERTA] El decodificador no es determinista.")

    # 3. Calibración
    print("\n--- Efecto de la Calibración ---")
    calib = meta.get("calibration_gain", 1.0)
    res_raw = res_rec / calib
    snr_raw = snr_global(orig, np.clip(base + res_raw, -1, 1))
    print(f"  Ganancia aplicada: {calib:.6f}")
    print(f"  SNR sin calibración: {snr_raw:.4f} dB")
    print(f"  SNR con calibración: {snr_enh_global:.4f} dB")
    print(f"  Aporte de la ganancia: {snr_enh_global - snr_raw:+.4f} dB")

if __name__ == "__main__":
    main()
