# Carpeta de Muestras (Samples)

Debido a derechos de autor, este repositorio no incluye archivos de audio reales.

Para ejecutar las pruebas (`tests/`), coloca aquí tu propio archivo `original.wav`:
- Formato: WAV PCM.
- Frecuencia de muestreo: 44.100 Hz.
- Canales: Estéreo (2 canales).
- Duración sugerida: 1 a 3 minutos.

El script `main.py` generará automáticamente el `base.mp3` y el `enhanced.wav` en esta misma carpeta.

# Entendiendo los archivos generados (`base.mp3` y `enhanced.wav`)

Para entender el flujo de trabajo de V25, es crucial comprender los tres archivos de audio que interactúan en el proceso:

### 1. `original.wav`
Es el archivo de entrada. Representa la señal de audio original de alta calidad (por ejemplo, un WAV sin pérdida). Es el "objetivo" que queremos alcanzar y se usa como referencia absoluta para calcular el error.

### 2. `base.mp3`
Es el archivo que se generaría usando un codificador MP3 convencional (LAME) a un bitrate específico (por ejemplo, 64 kbps).
- **¿Qué contiene?** El audio comprimido estándar, reproducido por cualquier reproductor del mundo.
- **¿Para qué sirve aquí?** Es el archivo en el que inyectamos los metadatos. Si un reproductor normal lo abre, escuchará solo esta capa base (retrocompatibilidad total). Si nuestro decodificador lo abre, extraerá los metadatos (los picos residuales) para mejorar el sonido.

### 3. `enhanced.wav`
Es el archivo de audio generado por nuestro **Decodificador V25**.
- **¿Cómo se crea?** El decodificador lee el `base.mp3`, decodifica la señal base, extrae el residual de los metadatos ID3, sintetiza el residual y lo suma a la señal base.
- **¿Para qué sirve?** Es la prueba de que nuestra reconstrucción funciona. Es la señal que se evalúa mediante SNR y distancia espectral contra el `original.wav`. En un entorno de producción, este audio sería reproducido directamente por un reproductor compatible con V25.
