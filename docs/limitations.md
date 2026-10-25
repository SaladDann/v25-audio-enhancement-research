# Limitaciones y Trabajo Futuro

## Lo que NO es V25
- No es un reemplazo de MP3.
- No es mejor que Opus (Opus a 64 kbps supera ampliamente a V25 a 88 kbps).
- No es un estándar.
- No garantiza mejora perceptual en todos los géneros musicales.

## Tareas Pendientes Críticas
1. **Resolver discrepancia de tamaño:** `main.py` reporta 643 KB de payload, pero `diagnose.py` lee 1029 KB del tag. (Hipótesis: diferencia entre tamaño binario comprimido vs tamaño Base64).
2. **Robustez:** Probar con voz humana y percusión (donde los picos cambian bruscamente).
3. **Seguridad de metadatos:** ¿Qué pasa si un usuario edita el MP3 en iTunes y borra los tags TXXX? El decodificador debe degradar gracefully al MP3 base.
4. **Calibración ciega:** Evitar calibrar y evaluar con exactamente el mismo fragmento de audio (overfitting).

## Comparativa Honesta
| Códec | Bitrate | Calidad estimada |
| :--- | :--- | :--- |
| MP3 Base | 64 kbps | Referencia |
| **V25** | **88.5 kbps** | **~MP3 75 kbps** |
| Opus | 64 kbps | ~MP3 128 kbps |
