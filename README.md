# Audio Enhancement — Investigación de una capa residual para mejorar MP3

**Estado:** Prototipo experimental V25
**Lenguaje:** Python
**Formato base:** MP3
**Capa de mejora:** Metadatos ID3 (etiquetas TXXX)

## 1. Resumen del proyecto

Este es un prototipo experimental de mejora de audio. Conserva un archivo MP3 convencional como capa base y añade información residual en sus metadatos para que un decodificador compatible pueda reconstruir una señal más próxima al audio original.

El sistema calcula la diferencia entre el audio original (WAV/FLAC) y la decodificación del MP3 base. Esta diferencia (residual) se representa extrayendo los picos espectrales dominantes en 12 bandas (un pico por banda, sin PNS). La información se almacena en etiquetas ID3 `TXXX`.

**Resultado principal registrado:** En la prueba actual, la reconstrucción obtuvo un SNR global de **20.3471 dB** frente a **19.1911 dB** del MP3 base (una mejora de **+1.1560 dB**), además de una reducción del 6.31% en la distancia espectral y un comportamiento determinista en las ejecuciones comparadas.

*Estos resultados corresponden al material y condiciones experimentales utilizadas. No demuestran todavía superioridad frente a Opus ni una mejora perceptual generalizada.*

## 2. ¿Qué problema intenta resolver?

La codificación con pérdida (como MP3) aproxima la señal original. Se investiga si es posible mantener la compatibilidad del MP3 y añadir una capa de información extra que permita recuperar parte de la diferencia perdida.

- \(x\): señal original.
- \(x_{\text{base}}\): señal del MP3 decodificado.
- \(r = x - x_{\text{base}}\): residual.
- \(\hat r\): residual aproximado reconstruido por V25.
- \(\hat x = x_{\text{base}} + \hat r\): señal mejorada.

## 3. Arquitectura experimental

### Flujo de codificación
1. Recibir audio original.
2. Codificar MP3 base (LAME).
3. Decodificar el MP3 para obtener la señal base real.
4. Calcular el residual (\(r\)).
5. Analizar el residual con el algoritmo V25 (picos espectrales).
6. Calcular la ganancia de calibración óptima para esa pista.
7. Empaquetar los datos en etiquetas ID3 `TXXX`.

### Flujo de decodificación
1. Leer el MP3 y decodificar la señal base.
2. Buscar etiquetas `ROWMP3_RESIDUAL_V25_*`.
3. Recuperar el payload.
4. Reconstruir el residual (IFFT + overlap-add Hann).
5. Aplicar la ganancia de calibración guardada.
6. Sumar el residual a la señal base.

*Un reproductor MP3 convencional ignorará los metadatos y reproducirá solo la capa base.*

## 4. Resultados cuantitativos (Prueba actual)

| Métrica | MP3 base | Reconstrucción V25 | Diferencia |
| :--- | :--- | :--- | :--- |
| **SNR global** | 19.1911 dB | 20.3471 dB | **+1.1560 dB** |
| **SNR canal 0** | 18.9712 dB | 20.0667 dB | +1.0955 dB |
| **SNR canal 1** | 19.4427 dB | 20.6729 dB | +1.2302 dB |
| **Distancia espectral** | 0.075530 | 0.070766 | -6.31 % |
| **Reproducibilidad** | — | Diferencia = 0.0 | Determinista |

*La calibración aportó +0.0146 dB (factor aplicado: 1.117530). El SNR global no coincide con la media aritmética por canal porque se calcula sobre energías agregadas.*

## 5. Limitaciones actuales

- **Evaluación limitada:** Resultados de un solo material de prueba.
- **Sin comparación con Opus:** Falta un estudio ciego con bitrate efectivo equivalente.
- **Percepción:** No hay pruebas auditivas controladas (A/B a volumen igualado).
- **Robustez:** No se ha probado con voz, percusión, transitorios o alta frecuencia.
- **Metadatos:** Programas de terceros pueden eliminar o alterar las etiquetas ID3.
- **Novedad científica:** La idea de "base + residual" es conocida (codificación escalable); la novedad algorítmica específica está por demostrar.

## 6. Próximos pasos

1. **Fase 1 (Reproducibilidad):** Resolver la discrepancia de tamaño de payload (643 KB vs 1029 KB, probablemente binario vs Base64).
2. **Fase 2 (Robustez):** Probar con 10 audios distintos (voz, rock, clásica).
3. **Fase 3 (Comparación):** Medir contra Opus a 88.5 kbps.
4. **Fase 4 (Convertidor):** Crear interfaz gráfica para automatizar el flujo.
5. **Fase 5 (Decodificador):** Plugin para VLC/foobar2000.

## 7. Estructura del repositorio

```text
v25-audio-enhancement/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── main.py
├── config.py                <-- Configuración global
├── encoder.py               <-- Codificador MP3 + extracción residual
├── decoder.py               <-- Decodificador y síntesis
├── sbr.py                   <-- Núcleo algorítmico (Picos y IFFT)
├── id3_payload.py           <-- Manejo de metadatos ID3v2 (TXXX)
├── metrics.py               <-- Cálculos de SNR y Distancia Espectral
├── docs/
│   ├── architecture.md
│   ├── experimental-results.md
│   ├── methodology.md
│   ├── limitations.md
│   └── software-engineering-analysis.md
├── tests/
│   ├── __init__.py
│   ├── validate_v25.py
│   ├── diagnose.py
│   ├── ablation_test.py
│   ├── stage_test.py
│   └── verify_alignment.py
└── samples/
    └── README.md
```

---

## 8. Reproducibilidad
Para verificar estos resultados, necesitas:

Python 3.11+

FFmpeg instalado (o usar static-ffmpeg)

Dependencias: pip install -r requirements.txt (numpy, scipy, soundfile, pydub, mutagen, lameenc, static-ffmpeg)

Un archivo WAV estéreo de 44.1 kHz (colócalo en samples/original.wav)

Para verificar estos resultados, necesitas:
- Python 3.11+
- Dependencias: `pip install -r requirements.txt`
- Un archivo WAV estéreo de 44.1 kHz (colócalo en `samples/original.wav`)

Ejecuta con terminal en ruta /src:
```bash
python main.py
```
---
Ejecutar cada prueba de validación (Opcional) desde la raiz del proyecto
```bash
python tests/validate_v25.py
python tests/diagnose.py
python tests/ablation_test.py
python tests/stage_test.py
python tests/verify_alignment.py
```
---
# Fundamentos
> *"V25 se apoya en el trabajo pionero de Scott Levine en modelado sinusoidal (1998) [citation:16], en la técnica de Overlap-Add de George & Smith (1997) [citation:14], y en el concepto de compatibilidad hacia atrás explorado por mp3PRO (Ziegler et al., 2002) [citation:22]. El proyecto ROW-mp3 de la Universidad de Stanford [citation:19] es el antecedente más directo de la idea de almacenar el residual en los tags ID3. Sin el estándar MP3 (ISO/IEC 11172-3) y sin el RFC 6716 de Opus [citation:11] como referencia de eficiencia, este proyecto no tendría ni base ni objetivo."*

## 9. Licencia
Licencia MIT

Este proyecto se publica como investigación experimental.
