# Entrega RC-0 — Grupo 7 / S-003

## Equipo y responsabilidades
| Integrante | Rol |
|---|---|
| Sebastian Pedro Aguirre Acosta | Integración |
| Karen Noelia Ramirez Quevedo | Percepción |
| Anahi Cortez Chinchay | Control |
| Valentino Uziel Vara Vargas | Planificación |

## Entorno
- Universidad ESAN, proyecto CapyTown, robot MicroROS-Pi5 / Yahboom.
- ROS 2 Humble en Docker (`ros2_dev`).
- `ROS_DOMAIN_ID=20`.
- Variante A1 — Torre: calibración.
- Variante A2 — Escalón: validación.

## Parámetros utilizados (calibraciones diferenciadas)
| Ensayo | Sentido | wheel_radius (m) | b_eff / wheel_separation (m) | Procedencia |
|---|---|---:|---:|---|
| Giro de 360° | Antihorario | 0.031584 | **0.27300** | Calibración direccional del equipo |
| Giro de 360° | Horario | 0.031584 | **0.25500** | Calibración direccional del equipo |
| Bonus de 720° | Antihorario | 0.031584 | **0.27400** | Valor de prueba comunicado por el equipo |

El archivo base `config/wheel_params.yaml` conserva `wheel_separation=0.27300` y `wheel_radius=0.031584`. El equipo cambió los valores temporalmente con `ros2 param set /odom_corrector wheel_separation VALOR`. **No se debe afirmar que hubo un solo valor constante de `b_eff` en todos los giros.**

El valor de 0.27400 para el bonus registra el parámetro utilizado; no demuestra por sí solo que el ensayo haya cumplido la tolerancia. El bonus requiere un giro físico de 720° con error ≤ 5° y una recta de 1 m con error ≤ 1 %, evaluados frente al docente.

## Mediciones de A2
| Prueba | Valor físico | Valor /odom | Error odométrico relativo |
|---|---:|---:|---:|
| Recta 1 | 0.998 m | 1.0027 m | 0.47 % |
| Recta 2 | 0.997 m | 1.0060 m | 0.90 % |
| Giro horario | 363° | 359.28° | 1.02 % |

La fórmula es `abs(valor_odom - valor_fisico) / abs(valor_fisico) * 100`.

## Resultados y documentación del RC-0
- Primera variante A1: calibración del radio y anchura de vía efectiva.
- Segunda variante A2: dos rectas y un giro horario.
- `plot_odom.py`: gráficas X-Y y orientación θ(t); reconoce SQLite3 o MCAP desde `metadata.yaml`.
- Evidencias: archivos CSV, carpetas rosbag2, imágenes PNG y `informe.pdf` de una página, compilados en el paquete actualizado de entrega del equipo.
- La recta A1 citada en el informe: 0.9670 m físicos, 0.9659 m /odom (0.11 %).
- Los cambios de `b_eff` por sentido hacen que la validación A2 no sea metodológicamente idéntica a una repetición con un único `b_eff` de A1, tal como exige el apartado D. Esta limitación debe presentarse al docente.

## Estado GitHub
Esta documentación acompaña el repositorio existente `anahicz/Robotica-RosCar`. No debe interpretarse como prueba de que se hayan cargado todos los rosbags, PNG o el PDF. El paquete completo debe verificarse y publicarse de manera separada antes de crear el tag `v1.0-rc0`.
