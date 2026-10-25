# Referencias y Fundamentos Teóricos

Este proyecto no habría sido posible sin el trabajo previo de investigadores y organismos de estandarización. A continuación se citan los estudios, estándares y documentos técnicos que fundamentan las decisiones de diseño de V25.

## 1. Codificación de Audio y Percepción (El MP3 Base)

El punto de partida de V25 es el estándar MP3 (MPEG-1 Audio Layer III). Su diseño psicoacústico y su estructura de frames son la base sobre la que se construye nuestra capa residual.

*   **ISO/IEC 11172-3 (MPEG-1 Audio):** El estándar original que define el MP3. V25 utiliza su estructura de frames y su decodificador base.
*   **Pan, D. (1995). "A Tutorial on MPEG/Audio Compression."** *IEEE MultiMedia*. Explica el modelo psicoacústico y la asignación de bits que hacen que el MP3 tenga un error (residual) predecible y estructurado.
*   **Evaluación Subjetiva del MP3:** Estudios como el de la AES (2009) demuestran que los oyentes prefieren la calidad CD sobre MP3 hasta 192 kbps, especialmente en géneros como la música acústica [citation:9]. Esto justifica por qué V25 se centra en bitrates bajos (64 kbps), donde el error es más audible y la mejora tiene más valor.

## 2. Modelado Sinusoidal y Representación de la Señal

La técnica de V25 para representar el residual (extraer picos espectrales) se basa en el **Modelado Sinusoidal**. La idea de que una señal de audio puede descomponerse en una suma de sinusoides (amplitud, frecuencia y fase) es fundamental en el procesamiento de audio.

*   **McAulay, R. J., & Quatieri, T. F. (1986). "Speech Analysis/Synthesis Based on a Sinusoidal Representation."** *IEEE Transactions on Acoustics, Speech, and Signal Processing*. El artículo fundacional que demostró que se puede analizar y sintetizar voz (y audio) mediante sinusoides.
*   **George, E. B., & Smith, M. J. T. (1997). "Speech Analysis/Synthesis and Modification Using an Analysis-by-Synthesis/Overlap-Add Sinusoidal Model."** *IEEE Transactions on Speech and Audio Processing*. Introduce la técnica de **Overlap-Add (OLA)** con ventanas (como la de Hann) que utilizamos en V25 para evitar el crujido y garantizar la continuidad entre frames [citation:14].
*   **Serra, X., & Smith, J. (1990). "Spectral Modeling Synthesis: A Sound Analysis/Synthesis System Based on a Deterministic Plus Stochastic Decomposition."** *Computer Music Journal*. Introduce la separación entre componentes tonales (picos sinusoidales) y estocásticos (ruido), que fue clave para entender por qué nuestro PNS (ruido) fallaba y los picos (tonos) funcionaban.

## 3. El Concepto de "Capa Residual" y Compatibilidad (Antecedente Directo)

La idea de guardar información extra en un MP3 sin romper la compatibilidad tiene precedentes muy claros que inspiradores de V25.

*   **mp3PRO y SBR (Spectral Band Replication):** Ziegler, T., Ehret, A., Ekstrand, P., & Lutzky, M. (2002). "Enhancing mp3 with SBR: Features and Capabilities of the new mp3PRO Algorithm." *AES 112th Convention*. Este es el antecedente más importante. mp3PRO usaba los datos auxiliares (*ancillary data*) del frame MP3 para guardar información de las frecuencias altas. Un decodificador viejo ignoraba esos datos; uno nuevo los usaba para "replicar" la banda alta [citation:10][citation:22]. V25 sigue la misma filosofía, pero en lugar de replicar agudos, codifica el error residual completo en los tags ID3.
*   **ROW-mp3 (Rate Optimization for MP3):** El proyecto de la Universidad de Stanford (Jieun Oh, Music 422) propuso exactamente lo que intentamos: **codificar el error entre el WAV original y el MP3, y guardarlo en el tag ID3**. Su implementación usaba ruido modelado (PNS) y demostró la viabilidad de la idea [citation:19][citation:23]. Nuestro V25 es una evolución de ROW-mp3 usando síntesis sinusoidal en frecuencia en lugar de ruido.

## 4. Sustitución de Ruido Perceptual (PNS) - (Descartates)

En las versiones V21-V24 intentamos usar PNS para el residual. Los papers nos ayudaron a entender por qué falló en nuestro caso y por qué los picos eran mejores.

*   **Schulz, D. (1996). "Improving Audio Codecs by Noise Substitution."** *Journal of the Audio Engineering Society*. El paper clásico que explica cómo reemplazar bandas de ruido con ruido sintético para ahorrar bits [citation:19]. V25 lo descartó porque, a diferencia de un códec perceptual, nuestro objetivo era reconstruir la **forma de onda** del error, no solo su energía.
*   **PNS en MP3 (ISO/IEC 11172-3):** El estándar MP3 original ya incluye PNS. Sin embargo, se usa para señales ruidosas, no para corregir el error de cuantización.

## 5. El Estado del Arte Actual: Opus

Para tener una vara de medir honesta, citamos el estándar que actualmente domina la eficiencia en compresión.

*   **RFC 6716 (Opus Codec):** El estándar de la IETF. Opus combina capas de Predicción Lineal (SILK) para voz y Transformada MDCT (CELT) para música [citation:11]. Su diseño híbrido le permite ser extremadamente eficiente a bitrates bajos (desde 6 kbps). V25 no compite con Opus en eficiencia, sino que explora un camino diferente: **la retrocompatibilidad con el legado MP3**.

## 6. Referencias de Ingeniería de Software

*   **Smith, S. W. (1997). "The Scientist and Engineer's Guide to Digital Signal Processing."** *California Technical Publishing*. La biblia para entender la FFT, la IFFT, el Teorema de Parseval (que usamos para escalar el ruido) y las ventanas de solapamiento.
*   **Levine, S. N. (1998). "Audio Representations for Data Compression and Compressed Domain Processing."** *Ph.D. Dissertation, Stanford University*. Tesis doctoral que inspiró el uso de modelado sinusoidal + ruido + transitorios y que sentó las bases de los códecs modernos [citation:16].

---
