"""
Módulo codificador. Orquesta la creación del MP3 base y la extracción del residual.
"""
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from sbr import compress_residual
from id3_payload import embed

def encode_base(wav_path: str, mp3_path: str, bitrate_kbps: int):
    """Codifica el WAV original a MP3 usando LAME."""
    AudioSegment.from_wav(wav_path).export(
        mp3_path, format="mp3", bitrate=f"{bitrate_kbps}k"
    )

def _decode_mp3_to_array(mp3_path: str) -> tuple[np.ndarray, int]:
    """Decodifica un MP3 a un array de Numpy normalizado entre -1.0 y 1.0."""
    audio = AudioSegment.from_mp3(mp3_path)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    max_val = float(np.max(np.abs(samples))) + 1e-9
    samples /= max_val
    if audio.channels == 2:
        samples = samples.reshape(-1, 2)
    return samples, audio.frame_rate

def encode(original_wav: str, base_mp3: str, cfg) -> dict:
    """
    Flujo principal de codificación:
    1. Crea el MP3 base.
    2. Decodifica para obtener el error real (residual).
    3. Comprime el residual y lo incrusta en el MP3.
    """
    # 1. Codificar MP3 base
    encode_base(original_wav, base_mp3, cfg.base_bitrate_kbps)

    # 2. Leer original y MP3 base para calcular residual
    orig, sr = sf.read(original_wav)
    if orig.ndim == 1:
        orig = np.stack([orig, orig], axis=1)

    base, _ = _decode_mp3_to_array(base_mp3)

    n = min(len(orig), len(base))
    orig, base = orig[:n], base[:n]
    residual = orig - base

    # 3. Comprimir residual y empaquetar
    meta = compress_residual(residual, base, sr, cfg)
    size = embed(base_mp3, meta, cfg.tag_desc)

    duration = n / sr
    return {
        "residual_bytes": size,
        "base_kbps": cfg.base_bitrate_kbps,
        "overhead_kbps": (size * 8) / duration / 1000,
    }
