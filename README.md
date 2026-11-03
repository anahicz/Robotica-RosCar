# RC-0 | CapyTown | Grupo 7 - Sección S-003

## Equipo y responsabilidades

| Integrante | Rol |
|---|---|
| Sebastian Pedro Aguirre Acosta | Integración |
| Karen Noelia Ramirez Quevedo | Percepción |
| Anahi Cortez Chinchay | Control |
| Valentino Uziel Vara Vargas | Planificación |

## Alcance
Primer arranque, calibración lineal y angular, validación en otra variante y generación de gráficas. A1: Torre (calibración). A2: Escalón (validación).

## Identificación
- Equipo: Grupo 7, sección S-003.
- Integrantes: **Sebastian Pedro Aguirre Acosta (Integración); Karen Noelia Ramirez Quevedo (Percepción); Anahi Cortez Chinchay (Control); Valentino Uziel Vara Vargas (Planificación)**.
- Plataforma: Yahboom MicroROS-Pi5; ROS 2 Humble; contenedor `ros2_dev`.
- `ROS_DOMAIN_ID`: 20 (configuración de proyecto que aparece en `setup_log.txt`).
- Nodos observados: `/YB_Car_Node` y `/odom_corrector`.
- `/odom`: aproximadamente 11 Hz; `/imu`: aproximadamente 25 Hz.

## Parámetros
`config/wheel_params.yaml` mantiene `wheel_radius=0.031584 m`, `wheel_separation=0.27300 m`; firmware: `r0=0.0325 m`, `b0=0.2400 m`. Valores experimentales según prueba: **antihorario 360°: `b_eff=0.27300 m`**; **horario 360°: `b_eff=0.25500 m`**; **bonus antihorario 720°: `b_eff=0.27400 m` (valor informado por el equipo, sin acreditación de precisión ni bonus frente al docente)**. Los cambios direccionales se aplicaron temporalmente mediante `ros2 param set`. El YAML conserva `0.27300 m` como valor base. **No se mantuvo un único `b_eff` en todos los giros; documentar esta salvedad en la defensa.**

## Organización del repositorio

| Ruta | Función |
|---|---|
| `capytown_esan/` | Paquete ROS 2 y sus módulos Python, launch y configuración |
| `scripts/` | Programas de prueba, calibración, análisis y compilación |
| `bags/` | Rosbags originales de A1 y A2 |
| `plots/` | Gráficas X-Y y θ(t) |
| `evidencias/` | Mediciones, diagnósticos y capturas |
| `config/` | Parámetros del robot |
| `docs/` | Guías, auditoría, documentación y notas de entrega |
| `informe.pdf` y CSV principales | Entregables solicitados por la rúbrica |
| `plot_odom.py` | Generador de gráficas |

**Importante:** `capytown_esan/capytown_esan/` es la estructura estándar del paquete ROS 2, no una duplicación que debamos eliminar. Se preservan las rutas del código y el lanzamiento para mantener la compatibilidad.

Los archivos Python y Shell llevan una cabecera de identificación del equipo responsable del repositorio; esta firma documental no sustituye ni inventa la autoría histórica individual.

## Evidencias y lectura de archivos
- `setup_log.txt`: arranque y frecuencias.
- `predicciones.txt`: predicciones antes de la práctica.
- `linea_recta.csv`: registros originales, normalizados solo en el número de columnas; respaldo literal en `evidencias/linea_recta_original.csv`.
- `calibration_log.csv`: historial original de `b_eff`; contiene valores previos que no coinciden completamente con el YAML adoptado.
- `validacion.csv`: A2 (dos rectas y giro horario), con mediciones físicas aportadas y errores relativos recalculados.
- `bags/`: A1 recta y giro; A2 dos rectas y giro horario. Los nombres conservan su procedencia y sus respectivos `metadata.yaml` y `.db3`.
- `plots/`: 12 PNG (pares X-Y y theta(t) por bag observado). Incluye giro antihorario suplementario de A2.
- `plot_odom.py`: lector de bolsas y generador de gráficas.
- `informe.pdf`: informe sintético de una página.
- `evidencias/`: diagnóstico y registros auxiliares, incluidos bonus no homologados presencialmente.

## Ejecución de plots (dentro de ros2_dev)
```bash
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install/setup.bash
export ROS_DOMAIN_ID=20
python3 plot_odom.py bags/rc0_recta1_V1
python3 plot_odom.py bags/rc0_giro_V1
python3 plot_odom.py bags/rc0_val_recta1
python3 plot_odom.py bags/rc0_val_recta2
python3 plot_odom.py bags/rc0_val_giro_horario1
```

## Criterios y advertencias
La recta A1 registrada en `linea_recta.csv` con 0.9670 m físicos y 0.9659 m odométricos tiene 0.11 % de error odométrico. A2 tiene 0.47 %, 0.90 % y 1.02 % (dos rectas, giro horario). Los datos de A1 y A2 no deben mezclarse con ensayos distintos.

El bonus requiere validación frente al docente: hay resultados de software marcados "SI" en dos archivos de giros 720°, pero no se considera acreditado por esa sola evidencia, y no hay evidencia equivalente suficiente de recta de bonus en el ZIP.

## Pendientes antes de presentar
1. Verificar la correspondencia de los rosbags con los valores físicos de cada prueba.
2. Confirmar si el docente acepta el cambio direccional temporal de b_eff en A2 o requiere repetir con el mismo valor de A1.
3. Revisar si la cátedra exige nombres canónicos exactos `rc0_recta`, `rc0_giro`, `rc0_val_recta`, `rc0_val_giro`; las carpetas de este paquete mantienen nombres reales para preservar trazabilidad.
4. El tag Git `v1.0-rc0` ya existe y conserva la versión original; esta revisión se publicará en commits posteriores.
