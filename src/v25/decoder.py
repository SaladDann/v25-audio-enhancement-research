"""
Módulo decodificador. Reconstruye el audio mejorado sumando el residual al MP3 base.
"""
import numpy as np
import soundfile as sf
from encoder import _decode_mp3_to_array
from sbr import decompress_residual
from id3_payload import extract

def decode(mp3_path: str, out_wav: str, cfg, enhanced: bool = True) -> str:
    """
    Decodifica el MP3. Si enhanced=True, busca el residual en los tags ID3,
    lo reconstruye y lo suma a la señal base.
    """
    base, sr = _decode_mp3_to_array(mp3_path)

    if not enhanced:
        sf.write(out_wav, base, sr)
        return "base"

    meta = extract(mp3_path, cfg.tag_desc)
    if meta is None:
        sf.write(out_wav, base, sr)
        return "base (sin residual)"

    residual = decompress_residual(meta, base, cfg)
    n = min(len(base), len(residual))
    out = np.clip(base[:n] + residual[:n], -1.0, 1.0)

    sf.write(out_wav, out, sr)
    return "enhanced"
