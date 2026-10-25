# Análisis de Ingeniería de Software y Habilidades Aplicadas

Este proyecto, aunque nació como una investigación sobre procesamiento de señales de audio (DSP) y compresión, requirió la aplicación práctica de múltiples conceptos de **Ingeniería de Software**. El desarrollo de V25 no fue solo un ejercicio de programación, sino un proceso de diseño de arquitectura, depuración sistemática y validación científica.

A continuación, se detallan las áreas de la ingeniería de software que se practicaron y consolidaron durante este proyecto.

## 1. Arquitectura de Software y Diseño de Sistemas
El sistema se diseñó bajo una arquitectura de **capas desacopladas** y **modularidad**, lo que permitió iterar rápidamente sin romper el sistema completo.

*   **Separación de responsabilidades (SoC):** El proyecto se dividió en módulos estrictos: codificación (`encoder.py`), procesamiento de señales (`sbr.py`), empaquetado (`id3_payload.py`), configuración global (`config.py`) y pruebas (`tests/`).
*   **Diseño de Interfaces:** Se definieron estructuras de datos claras (diccionarios de metadatos, payloads binarios) para que el codificador y el decodificador se comunicaran sin acoplarse.
*   **Patrón de Diseño "Enhancement Layer":** Se implementó una arquitectura de capa base + capa de mejora (residual), un concepto de ingeniería utilizado en códecs escalables modernos.

## 2. Procesamiento de Datos y Serialización
*   **Serialización Binaria:** Se diseñó un formato de empaquetado estricto utilizando la librería `struct` de Python. Se definieron tamaños exactos en bits/bytes (ej. 6 bits para frecuencia, 8 bits para magnitud) para maximizar la eficiencia.
*   **Compresión y Codificación:** Uso de `zlib` y `lzma` para compresión, y `base64` para evadir restricciones de texto en los metadatos ID3.
*   **Manejo de Grandes Volúmenes de Datos:** Procesamiento de arreglos de decenas de millones de muestras utilizando `numpy` para operaciones vectorizadas (FFT, IFFT, overlap-add).

## 3. Depuración (Debugging) y Solución de Problemas
Esta fue una de las áreas más intensas. El sistema pasó por más de 20 iteraciones (V1 a V25). Se aplicaron técnicas avanzadas de depuración:
*   **Diagnóstico Basado en Hipótesis:** En lugar de cambiar código a ciegas, se formulaban hipótesis (ej. "el error está en la fase" o "el ID3 trunca los datos") y se creaban scripts específicos para validarlas o refutarlas.
*   **Pruebas de Aislamiento (Ablation Testing):** Se apagaron partes del sistema (ej. desactivar PNS o apagar la calibración) para medir el impacto exacto de cada componente en el resultado final.
*   **Análisis de Errores Matemáticos:** Detección de bugs sutiles como la doble acumulación de fase, el truncamiento de bytes por caracteres NUL en texto Latin-1, y la discrepancia de escalas entre la FFT de análisis y síntesis.

## 4. Validación, Pruebas y Aseguramiento de Calidad (QA)
*   **Desarrollo Guiado por Pruebas (TDD adaptado):** Se crearon múltiples scripts de validación (`diagnose.py`, `stage_test.py`, `verify_alignment.py`, `ablation_test.py`) para verificar que el código hiciera exactamente lo que debía en cada etapa.
*   **Pruebas de Regresión:** Cada vez que se cambiaba el núcleo del algoritmo, se volvían a ejecutar todas las pruebas para asegurar que no se rompieran las mejoras anteriores.
*   **Verificación de Determinismo:** Se implementaron pruebas para garantizar que el decodificador genere la misma señal exacta ante las mismas entradas, una propiedad crítica en sistemas de audio.
*   **Auditoría de Datos:** Verificación de que los metadatos guardados y leídos fueran matemáticamente idénticos (diferencia RMS = 0).

## 5. Gestión de la Configuración y Entornos
*   **Manejo de Dependencias:** Uso de entornos virtuales y archivos `requirements.txt`.
*   **Portabilidad de Herramientas:** Integración de binarios externos (FFmpeg) empaquetados como dependencias del proyecto (`static-ffmpeg`) para evitar la clásica pesadilla de "funciona en mi máquina" (It works on my machine).

## 6. Investigación Científica aplicada al Software
*   **Análisis de Métricas Objetivas:** Implementación de cálculos matemáticos para evaluar la calidad (SNR, Distancia Espectral, Correlación de Pearson).
*   **Documentación Técnica Rigurosa:** Redacción de memorias técnicas distinguiendo lo demostrado empíricamente de lo que es hipótesis o trabajo futuro.
*   **Ética de Datos:** Reconocimiento de las limitaciones del prototipo (no sobreestimar los resultados) y planteamiento de comparaciones justas contra estándares de la industria (Opus).

## Conclusión
Este proyecto demuestra que la ingeniería de software no se trata únicamente de escribir sintaxis, sino de **diseñar arquitecturas robustas, iterar sobre fallos, aislar variables y validar resultados con evidencia**. El proceso de llevar un prototipo desde una idea conceptual que fallaba (-1.5 dB) hasta una versión funcional y validada (+1.15 dB) es un ejemplo práctico de resolución de problemas de ingeniería.
