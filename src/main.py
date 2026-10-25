"""
Punto de entrada principal para el pipeline de V25.
Orquesta la codificación del MP3 base, la extracción del residual,
la decodificación mejorada y la evaluación de métricas.
"""
import sys
import os

# 1. Configurar el PATH para que Python encuentre los módulos dentro de 'v25'
current_dir = os.path.dirname(os.path.abspath(__file__))
v25_dir = os.path.join(current_dir, 'v25')
sys.path.append(v25_dir)

import static_ffmpeg
static_ffmpeg.add_paths()

from config import CFG
from encoder import encode
from decoder import decode
from metrics import report

def main():
    # 2. Configurar rutas absolutas hacia la carpeta 'samples' en la raíz del proyecto
    root_dir = os.path.abspath(os.path.join(current_dir, '..'))
    samples_dir = os.path.join(root_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)

    # Actualizar la configuración global con las rutas correctas
    CFG.original_wav = os.path.join(samples_dir, "original.wav")
    CFG.base_mp3 = os.path.join(samples_dir, "base.mp3")
    CFG.enhanced_wav = os.path.join(samples_dir, "enhanced.wav")

    # 3. Validación de entrada (Fail-fast principle)
    if not os.path.exists(CFG.original_wav):
        print("\n[ERROR] No se encontró el archivo de entrada.")
        print(f"Por favor, coloca un archivo WAV estéreo de 44.1 kHz en:")
        print(f"  --> {CFG.original_wav}")
        print("Y vuelve a ejecutar el script.\n")
        sys.exit(1)

    print("==================================================")
    print("       V25 AUDIO ENHANCEMENT PIPELINE")
    print("==================================================\n")

    # --- FASE 1: CODIFICACIÓN ---
    print("[1/3] Codificando MP3 base y extrayendo residual...")
    info = encode(CFG.original_wav, CFG.base_mp3, CFG)

    print(f"      ├─ Bitrate base:      {info['base_kbps']} kbps")
    print(f"      ├─ Tamaño residual:   {info['residual_bytes']} bytes")
    print(f"      ├─ Overhead:          {info['overhead_kbps']:.2f} kbps")
    print(f"      └─ Bitrate efectivo:  {info['base_kbps'] + info['overhead_kbps']:.1f} kbps\n")

    # --- FASE 2: DECODIFICACIÓN ---
    print("[2/3] Decodificando y sintetizando audio mejorado...")
    mode = decode(CFG.base_mp3, CFG.enhanced_wav, CFG, enhanced=True)
    print(f"      └─ Estado: {mode}\n")

    # --- FASE 3: MÉTRICAS ---
    print("[3/3] Evaluando métricas objetivas de calidad...")
    m = report(CFG.original_wav, CFG.base_mp3, CFG.enhanced_wav, CFG)

    snr_base = m['SNR_base_dB']
    snr_enh = m['SNR_enhanced_dB']
    delta_snr = snr_enh - snr_base

    print(f"      ├─ SNR Base:          {snr_base:.2f} dB")
    print(f"      ├─ SNR V25:           {snr_enh:.2f} dB  (Delta: {delta_snr:+.2f} dB)")
    print(f"      ├─ Dist. Base:        {m['SpecDist_base']:.4f}")
    print(f"      └─ Dist. V25:         {m['SpecDist_enhanced']:.4f}\n")

    print("==================================================")
    if delta_snr > 0:
        print(f" [ÉXITO] V25 supera al MP3 base por {delta_snr:.2f} dB.")
    else:
        print(f" [ALERTA] V25 no superó al base (Delta: {delta_snr:.2f} dB).")
    print("==================================================\n")

if __name__ == "__main__":
    main()
