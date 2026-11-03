# Auditoría de la entrega RC-0 (archivo de trabajo)

## Evidencias verificadas del ZIP
- Arranque, nodos y frecuencias: `setup_log.txt`.
- Predicciones iniciales: `predicciones.txt`.
- Gráficas disponibles: 12 PNG, organizadas para A1 y A2.
- Bolsas conservadas en la entrega: dos de A1 (recta y giro) y tres de A2 (dos rectas y giro horario).
- Tabla de calibración angular: 22 registros en `calibration_log.csv`.
- Tabla lineal: mezcla ensayos de distintas condiciones y contiene dos comas finales adicionales en el original; la copia en raíz solo normaliza el formato de cinco columnas.
- Validación A2: mediciones físicas 0.998 m, 0.997 m y 363 grados; odometrías 1.0027 m, 1.0060 m y 359.28 grados.

## Precauciones de interpretación
1. El error frente al objetivo (por ejemplo 360 grados) no es lo mismo que el error relativo entre `/odom` y el valor físico.
2. La salida de diagnóstico usa la distancia entre extremos para algunas rectas; el `valor_odom` en validacion.csv mantiene exactamente esos valores documentados en la conversación.
3. Giro 360° antihorario: `b_eff=0.27300`; giro 360° horario (A2): `b_eff=0.25500`; bonus 720° antihorario: `b_eff=0.27400` según la aclaración del equipo. El YAML base conserva `0.27300`. No es válido afirmar un único b_eff en todos los sentidos.
4. El historial bonus 720 incluye valores que cumplen tolerancia física, pero el criterio solo se acredita con prueba frente al profesor.
5. La recta repetida A1 con medida física reportada de 95.2 cm frente a aproximadamente 1 m odométrico no está asociada de manera inequívoca a un bag del ZIP. No se reemplaza el resultado A1 documentado por un ensayo no emparejado.
6. No se documentó el nombre o rol preciso de los cuatro integrantes del equipo en el ZIP auditado.

## Qué queda pendiente
- Revisar ortografía final de los nombres en README.
- Confirmación de política de b_eff direccional con docente.
- Publicar a repositorio y etiquetar `v1.0-rc0` una vez confirmado.
