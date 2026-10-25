"""
Configuración global para el códec experimental V25.
Define los parámetros de análisis, síntesis y empaquetado.
"""
from dataclasses import dataclass

@dataclass
class Config:
    # --- Parámetros del MP3 Base ---
    base_bitrate_kbps: int = 64  # Bitrate del archivo MP3 sobre el que se calcula el residual

    # --- Parámetros de Análisis STFT (Short-Time Fourier Transform) ---
    frame_ms: int = 40           # Tamaño de la ventana de análisis en milisegundos
    hop_ratio: float = 0.5       # Salto entre ventanas (0.5 = 50% de solapamiento)

    # --- Definición de Bandas Espectrales ---
    n_bands: int = 12            # Número de bandas geométricas para agrupar los picos
    band_min_hz: float = 100.0   # Frecuencia mínima de análisis
    band_max_hz: float = 16000.0 # Frecuencia máxima de análisis

    # --- Representación del Residual ---
    n_peaks_per_band: int = 1    # Cuántos picos extraer por banda (V25 usa 1)

    # --- Empaquetado ID3 ---
    max_chunk_bytes: int = 32 * 1024 # Tamaño máximo de cada chunk TXXX antes de comprimir
    max_raw_chunk: int = 128 * 1024  # Tamaño máximo de datos crudos antes de comprimir

    # --- Identificadores ---
    tag_desc: str = "ROWMP3_RESIDUAL_V25" # Prefijo para los tags TXXX en el MP3

    # Rutas por defecto para pruebas locales
    original_wav: str = "samples/original.wav"
    base_mp3: str = "samples/base.mp3"
    enhanced_wav: str = "samples/enhanced.wav"

# Instancia global de configuración
CFG = Config()
