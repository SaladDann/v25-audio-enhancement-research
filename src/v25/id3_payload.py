"""
Gestión del almacenamiento del residual en metadatos ID3v2.
Utiliza compresión LZMA y codificación Base64 para evitar truncamientos con bytes NUL.
"""
import base64
import lzma
import pickle
import numpy as np
from mutagen.id3 import ID3, TXXX

def embed(mp3_path: str, meta: dict, tag_desc: str) -> int:
    """
    Empaqueta el payload y los metadatos en múltiples tags TXXX.
    Retorna el tamaño total en bytes del payload comprimido.
    """
    # 1. Empaquetar cabecera
    header = {
        "bands": meta["bands"].tolist(),
        "frame_len": meta["frame_len"],
        "hop": meta["hop"],
        "sr": meta["sr"],
        "n_samples": meta["n_samples"],
        "channels": meta["channels"],
        "calibration_gain": float(meta.get("calibration_gain", 1.0)),
        "per_channel_gains": [float(g) for g in meta.get("per_channel_gains", [])],
    }
    header_comp = lzma.compress(pickle.dumps(header, protocol=4), preset=6)

    # 2. Dividir y comprimir payload
    payload = meta["payload"]
    max_raw = meta.get("max_raw_chunk", 128 * 1024)
    chunks = []
    for i in range(0, len(payload), max_raw):
        chunks.append(lzma.compress(payload[i:i + max_raw], preset=6))

    all_chunks = [header_comp] + chunks

    # 3. Escribir en el archivo
    try:
        tags = ID3(mp3_path)
    except Exception:
        tags = ID3()

    # Limpiar tags previos con este prefijo
    for key in list(tags.keys()):
        if key.startswith("TXXX:" + tag_desc):
            del tags[key]

    total_bytes = 0
    for idx, comp in enumerate(all_chunks):
        b64 = base64.b64encode(comp).decode("ascii")
        tags.add(TXXX(encoding=3, desc=f"{tag_desc}_{idx:04d}", text=[b64]))
        total_bytes += len(comp)

    tags.add(TXXX(encoding=3, desc=f"{tag_desc}_END", text=[str(len(all_chunks))]))
    tags.save(mp3_path)

    return total_bytes

def extract(mp3_path: str, tag_desc: str) -> dict | None:
    """
    Extrae y descomprime el payload desde los tags ID3.
    Retorna None si no se encuentran los tags o están corruptos.
    """
    try:
        tags = ID3(mp3_path)
    except Exception:
        return None

    end_key = "TXXX:" + tag_desc + "_END"
    if end_key not in tags:
        return None

    try:
        n_chunks = int(tags[end_key].text[0])
    except Exception:
        return None

    chunks = []
    for i in range(n_chunks):
        key = f"TXXX:{tag_desc}_{i:04d}"
        if key not in tags:
            return None
        try:
            comp = base64.b64decode(tags[key].text[0])
            chunks.append(lzma.decompress(comp))
        except Exception:
            return None

    if not chunks:
        return None

    try:
        header = pickle.loads(chunks[0])
    except Exception:
        return None

    header["bands"] = np.array(header["bands"], dtype=np.float32)
    header["payload"] = b"".join(chunks[1:])

    return header
