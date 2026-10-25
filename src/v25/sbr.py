"""
Módulo de procesamiento de señales y codificación del residual.
Implementa la extracción de picos espectrales y la síntesis por IFFT + Overlap-Add.
"""
import numpy as np
import struct

def _as_2d(x: np.ndarray) -> np.ndarray:
    """Asegura que el array de audio tenga forma (N, channels)."""
    return x if x.ndim == 2 else np.stack([x, x], axis=1)

def _hann(n: int) -> np.ndarray:
    """Genera una ventana de Hann simétrica."""
    return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / n)

def _pack_peak(k: int, f6: int, m6: int, p6: int, maxq: int) -> bytes:
    """
    Empaqueta un pico espectral en 4 bytes (32 bits).
    Distribución: 4 bits (banda) + 6 bits (frecuencia) + 6 bits (magnitud rel)
                  + 6 bits (fase) + 8 bits (magnitud absoluta log).
    """
    v = (k & 0x0F) | ((f6 & 0x3F) << 4) | ((m6 & 0x3F) << 10) | ((p6 & 0x3F) << 16) | ((maxq & 0xFF) << 22)
    return struct.pack("<I", v)

def _unpack_peak(b: bytes, pos: int) -> tuple:
    """Desempaqueta 4 bytes en sus 5 componentes (banda, freq, mag_rel, fase, maxq)."""
    v = struct.unpack_from("<I", b, pos)[0]
    return (v & 0x0F, (v >> 4) & 0x3F, (v >> 10) & 0x3F, (v >> 16) & 0x3F, (v >> 22) & 0xFF)

def compress_residual(residual: np.ndarray, base: np.ndarray, sr: int, cfg) -> dict:
    """
    Extrae los picos dominantes del residual y calcula la ganancia de calibración.
    Retorna un diccionario con el payload binario y los metadatos del frame.
    """
    r = _as_2d(residual)
    n = min(len(r), len(base))
    r = r[:n]
    channels = r.shape[1]

    frame_len = int(sr * cfg.frame_ms / 1000)
    hop = max(1, int(frame_len * cfg.hop_ratio))
    n_frames = max(1, 1 + (n - frame_len) // hop)

    # Bandas geométricas
    bands = np.geomspace(cfg.band_min_hz, min(cfg.band_max_hz, sr / 2), cfg.n_bands + 1)
    freqs = np.fft.rfftfreq(frame_len, 1 / sr)
    n_bands = cfg.n_bands

    all_frames = []
    for c in range(channels):
        ch_frames = []
        rc = r[:, c]
        for i in range(n_frames):
            start = i * hop
            rf = rc[start:start + frame_len]
            if len(rf) < frame_len:
                rf = np.pad(rf, (0, frame_len - len(rf)))
            Rf = np.fft.rfft(rf)

            frame_peaks = []
            for k in range(n_bands):
                m = (freqs >= bands[k]) & (freqs < bands[k + 1])
                if not m.any():
                    continue
                idx = np.where(m)[0]
                mags = np.abs(Rf[idx])
                if len(mags) == 0 or mags.max() <= 0:
                    continue

                # Extraer el pico máximo de esta banda
                top = idx[int(np.argmax(mags))]
                mag = float(np.abs(Rf[top]))
                f_bin = float(freqs[top])
                ph = float(np.angle(Rf[top]))

                # Cuantización (6 bits freq, 6 bits fase, 8 bits magnitud)
                bw = bands[k + 1] - bands[k]
                f_norm = (f_bin - bands[k]) / (bw + 1e-9)
                f6 = int(np.clip(f_norm * 63, 0, 63))
                m6 = 63 # Redundante por ahora, reservado para futuro
                p6 = int(np.clip((ph + np.pi) / (2 * np.pi) * 63, 0, 63))
                maxq = int(np.clip(np.log10(mag + 1e-9) * 20 + 128, 0, 255))

                frame_peaks.append((k, f6, m6, p6, maxq))
            ch_frames.append(frame_peaks)
        all_frames.append(ch_frames)

    # Calibración de amplitud
    res_rec = _synthesize(all_frames, bands, frame_len, hop, sr, n, channels, 1.0)
    r_real = r[:n]

    gains = []
    for c in range(channels):
        denom = float(np.sum(res_rec[:, c] ** 2)) + 1e-12
        g = float(np.sum(r_real[:, c] * res_rec[:, c]) / denom)
        gains.append(g if np.isfinite(g) and g > 0 else 1.0)

    payload = _serialize(all_frames, cfg)

    return {
        "payload": payload,
        "bands": bands.astype(np.float32),
        "frame_len": frame_len,
        "hop": hop,
        "sr": sr,
        "n_samples": n,
        "channels": channels,
        "calibration_gain": float(np.mean(gains)),
        "per_channel_gains": gains,
    }

def _serialize(all_frames: list, cfg) -> bytes:
    """Serializa la estructura de picos a bytes binarios compactos."""
    out = bytearray()
    out += struct.pack("<BBB", cfg.n_bands, cfg.n_peaks_per_band, len(all_frames))
    for ch in all_frames:
        out += struct.pack("<I", len(ch))
        for frame in ch:
            out += struct.pack("<B", len(frame))
            for peak in frame:
                out += _pack_peak(*peak)
    return bytes(out)

def _deserialize(payload: bytes) -> dict:
    """Reconstruye la estructura de picos desde bytes."""
    pos = 0
    n_bands, npb, channels = struct.unpack_from("<BBB", payload, pos); pos += 3
    all_frames = []
    for c in range(channels):
        n_frames = struct.unpack_from("<I", payload, pos)[0]; pos += 4
        ch = []
        for _ in range(n_frames):
            n_p = payload[pos]; pos += 1
            frame = []
            for _ in range(n_p):
                frame.append(_unpack_peak(payload, pos))
                pos += 4
            ch.append(frame)
        all_frames.append(ch)
    return {"all_frames": all_frames, "n_bands": n_bands, "channels": channels}

def _synthesize(all_frames, bands, frame_len, hop, sr, n_samples, channels, gain) -> np.ndarray:
    """
    Sintetiza el residual en el dominio de la frecuencia (IFFT) usando Overlap-Add.
    Esta técnica elimina los errores de acumulación de fase del dominio temporal.
    """
    freqs = np.fft.rfftfreq(frame_len, 1 / sr)
    window = _hann(frame_len)
    out = np.zeros((n_samples + frame_len, channels), dtype=np.float32)

    for c in range(channels):
        for i, frame_peaks in enumerate(all_frames[c]):
            start = i * hop
            if start >= n_samples + frame_len:
                break

            # Construir espectro complejo
            spec = np.zeros(len(freqs), dtype=np.complex128)
            for (k, f6, m6, p6, maxq) in frame_peaks:
                bw = bands[k + 1] - bands[k]
                f_hz = bands[k] + (f6 / 63.0) * bw
                mag = 10 ** ((maxq - 128) / 20.0)
                ph = (p6 / 63.0) * 2 * np.pi - np.pi
                bin_idx = int(np.argmin(np.abs(freqs - f_hz)))
                spec[bin_idx] += mag * np.exp(1j * ph)

            # IFFT y aplicar ventana
            rec = np.fft.irfft(spec, n=frame_len).astype(np.float32) * window
            out[start:start + frame_len, c] += rec

    # Normalización Overlap-Add
    win_sum = np.zeros(n_samples + frame_len, dtype=np.float32)
    for i in range(len(all_frames[0])):
        start = i * hop
        end = min(start + frame_len, n_samples + frame_len)
        win_sum[start:end] += window[:end - start]
    win_sum = np.maximum(win_sum, 1e-6)

    return (out / win_sum[:, None])[:n_samples] * gain

def decompress_residual(meta: dict, base: np.ndarray, cfg) -> np.ndarray:
    """
    Punto de entrada para la decodificación.
    Reconstruye el residual a partir del payload y aplica la calibración.
    """
    d = _deserialize(meta["payload"])
    res = _synthesize(
        d["all_frames"], meta["bands"], meta["frame_len"],
        meta["hop"], meta["sr"], meta["n_samples"], meta["channels"],
        meta.get("calibration_gain", 1.0)
    )
    return res
