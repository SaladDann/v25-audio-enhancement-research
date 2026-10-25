# Arquitectura Técnica

## Visión general
V25 no es un códec nuevo, es una **capa de mejora (enhancement layer)**. Utiliza el estándar MP3 como capa base y añade información en los tags ID3v2 (frames `TXXX`).

## El Codificador (Encoder)
1. **Análisis STFT:** Se divide el audio en ventanas de 40 ms (1764 muestras a 44.1kHz) con 50% de solapamiento (hop de 882 muestras).
2. **Selección de picos:** En 12 bandas geométricas (100 Hz a 16 kHz), se busca el bin de máxima magnitud.
3. **Cuantización:**
   - Frecuencia: 6 bits (64 niveles, logarítmico dentro de la banda).
   - Magnitud: 8 bits (`maxq`, escala logarítmica).
   - Fase: 6 bits (64 niveles).
4. **Calibración:** Se calcula la ganancia óptima (\(a^* = \frac{\sum r \cdot \hat r}{\sum \hat r^2}\)) comparando el residual real con la síntesis de los picos. Se guarda en el header.
5. **Empaquetado:** Los datos se serializan en binario, se comprimen con LZMA, se codifican en Base64 y se dividen en chunks de ~100 KB en los tags `TXXX` (para evitar truncamiento).

## El Decodificador (Decoder)
1. **Lectura ID3:** Busca los tags `ROWMP3_RESIDUAL_XXXX` y `_END`.
2. **Deserialización:** Extrae y descomprime el payload.
3. **Síntesis (Clave del éxito):** En lugar de generar sinusoides en el tiempo (que acumulaba error de fase), se construye un espectro complejo por cada frame:
   - Se coloca cada pico en su bin FFT más cercano con su magnitud y fase.
   - Se aplica IFFT.
   - Se multiplica por ventana Hann y se hace **Overlap-Add**.
4. **Calibración:** Se multiplica la señal resultante por la ganancia guardada.
5. **Suma:** Se añade a la señal del MP3 base.

## Formato del Payload
```text
[Cabecera LZMA]
  n_bands: 1 byte (12)
  n_peaks_per_band: 1 byte (1)
  channels: 1 byte (2)
  calibration_gain: float32
[Payload]
  Por canal:
    n_frames: uint32
    Por frame:
      n_peaks: uint8
      Por pico: 5 bytes (k, freq, mag, phase, maxq)
