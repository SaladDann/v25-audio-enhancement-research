# Resultados Experimentales (V25)

## Entorno de Prueba
- Audio: Estéreo, 44.1 kHz, 9,262,778 muestras (aprox. 3.5 minutos).
- Codificador base: LAME MP3 a 64 kbps.
- Overhead: ~24.49 kbps (payload comprimido).

## Tabla Comparativa

| Configuración | SNR Global | Delta vs Base | Correlación Residual |
| :--- | :--- | :--- | :--- |
| MP3 Base (64 kbps) | 19.19 dB | 0.00 dB | — |
| V25 (Híbrido Picos+PNS) | 18.73 dB | -0.46 dB | 0.25 |
| **V25 (Picos puros)** | **20.35 dB** | **+1.16 dB** | **0.47** |

## Hallazgos Clave
1. **PNS es perjudicial:** El ruido sintético no correlaciona con el residual real (correlación ~0). Solo añade energía de error.
2. **La síntesis en frecuencia funciona:** Pasar de sinusoides a IFFT+Overlap-Add multiplicó por 28 la correlación temporal (0.009 a 0.254).
3. **La calibración es estable:** La ganancia óptima ronda 1.11 - 1.12. El codificador la calcula automáticamente.
4. **El límite físico:** A 64 kbps, el residual es muy denso en altas frecuencias (se necesitan 117 bins para el 90% de la energía en la banda 10-16 kHz). Con 1 pico por banda, capturamos ~40% de la energía total, pero la suficiente para mejorar el SNR.
