# Metodología y Métricas

## Definición del Residual
El residual se calcula en el dominio del tiempo después de alinear las señales:
\(r[n] = x[n] - x_{\text{base}}[n]\)

## Métricas de Evaluación
1. **SNR Global:**
   \(SNR = 10 \log_{10} \left( \frac{\sum x^2}{\sum (x - \hat{x})^2} \right)\)
2. **Distancia Espectral:**
   Usa STFT (n_fft=2048). Normaliza las magnitudes y calcula la norma L2 de la diferencia.
3. **Correlación de Pearson:**
   Mide la similitud de forma de onda entre \(r\) y \(\hat{r}\).

## Protocolo de Validación
- El script `validate.py` comprueba la consistencia de las métricas.
- El script `ablation_test.py` aísla el efecto de los picos vs el ruido (PNS).
- El script `verify_alignment.py` asegura que el codificador y decodificador ven exactamente las mismas muestras (diferencia = 0).
