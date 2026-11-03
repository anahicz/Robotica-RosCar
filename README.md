# Robotica-RosCar

Proyecto académico de Robótica de la Universidad ESAN, desarrollado con el robot **MicroROS-Pi5 Robot Car** dentro del proyecto **CapyTown**.

Este repositorio reunirá el código, las configuraciones, la documentación y las evidencias de las pruebas realizadas durante el curso. El trabajo se desarrollará mediante conexión remota al entorno Linux de la Raspberry Pi 5 y el uso de ROS 2 Humble en Docker.

**Etapa actual:** RC-0 — Primer arranque y calibración del robot.  
**Periodo académico:** 2026-2.  
**Sección:** S-003.  
**Estado:** RC-0 ejecutado: arranque, calibración A1, validación A2 y gráficas. Evidencias y límites metodológicos en `docs/rc0_entrega_grupo7.md`.

## Puesta en marcha de la Parte A

El paquete propio `capytown_esan` incorpora un adaptador de `/odom_raw` a `/odom` y `/tf`, utilizando el agente micro-ROS que ya está activo en otro contenedor. La [guía de Parte A](docs/parte_a.md) explica la instalación sin Internet en el carro, la función de cada archivo y las verificaciones pendientes. El estado inicial observado está en [setup_log.txt](setup_log.txt).

Esta versión conserva la odometría de origen. Las calibraciones de `r` y `b_eff` se desarrollarán después de comprobar cómo se aplican al modelo real del robot.

## Objetivo

Poner en funcionamiento el robot, comprobar la comunicación entre la placa controladora y ROS 2, y calibrar los parámetros que permiten estimar la distancia recorrida y el ángulo de giro.

La calibración compara el movimiento medido físicamente con la odometría del robot. Esta base permitirá desarrollar las siguientes etapas del proyecto con parámetros obtenidos experimentalmente.

## Plataforma de trabajo

| Componente | Función |
| --- | --- |
| MicroROS-Pi5 Robot Car | Plataforma móvil de cuatro ruedas utilizada en las pruebas. |
| Raspberry Pi 5 y Linux | Computadora y sistema operativo del robot. |
| Docker | Entorno de ejecución de ROS 2 Humble y sus dependencias. |
| ROS 2 Humble | Comunicación entre los programas mediante nodos y tópicos. |
| Placa controladora y micro-ROS | Interacción con los motores y sensores mediante el firmware del robot. |
| Agente micro-ROS | Enlace entre los nodos de la placa y la red de ROS 2. |
| Python y rosbag2 | Desarrollo de herramientas, registro de mensajes y análisis de las pruebas. |
| Git y GitHub | Control de versiones y documentación del trabajo del equipo. |

## Alcance de RC-0

En esta etapa se realizarán las siguientes actividades:

- Verificar la comunicación de la placa con ROS 2 y la presencia de `/cmd_vel`, `/odom`, `/imu` y `/scan`.
- Configurar el `ROS_DOMAIN_ID` correspondiente al grupo y comprobar el aislamiento respecto a otros equipos.
- Registrar las frecuencias de publicación de `/odom` y `/imu`.
- Calibrar el radio de rueda `r` mediante pruebas en línea recta.
- Calibrar el ancho de vía efectivo `b_eff` mediante giros en sitio.
- Validar los parámetros en una segunda variante del escenario.
- Grabar las pruebas y generar gráficas de trayectoria y orientación.

El cuadrado en lazo abierto y la fusión con IMU corresponden a RC-1; cámara y carril, a RC-2; y LiDAR, a RC-3 en adelante. En RC-0 se comprueba la presencia de los tópicos requeridos, aunque todavía no se desarrollan esas funciones.

## Conceptos principales

| Concepto | Significado |
| --- | --- |
| `/cmd_vel` | Tópico que recibe las órdenes de velocidad lineal y angular. |
| `/odom` | Tópico que publica la estimación de posición y orientación del robot. |
| `r` | Radio de rueda utilizado por el modelo para relacionar el giro de las ruedas con la distancia. |
| `b_eff` | Separación efectiva entre ambos lados del robot utilizada para modelar el giro. |
| Bag | Carpeta que almacena mensajes de ROS 2 y sus metadatos para analizarlos posteriormente. |

Aunque tiene cuatro ruedas, el reto utiliza un modelo diferencial equivalente: el movimiento depende de las velocidades de los lados izquierdo y derecho.

## Flujo de trabajo

Para la sección S-003, la calibración se realiza en **A1 — Torre** y la validación en **A2 — Escalón**.

| Etapa | Actividad | Criterio previsto |
| --- | --- | --- |
| Predicción | Registrar las respuestas antes de encender el robot y realizar mediciones. | Conservar las predicciones originales. |
| Arranque | Comprobar el entorno, el agente, el dominio y los tópicos. | Comunicación y frecuencias documentadas. |
| Recta | Realizar tres corridas y ajustar únicamente `r`. | Error final de distancia ≤ 2 %. |
| Giro | Mantener `r` fijo y ajustar `b_eff` con giros de 360°. | Error angular < 1 %. |
| Validación | Realizar dos rectas y un giro en A2. | Mantener los parámetros sin recalibrar. |
| Análisis | Leer los bags y generar las gráficas. | Trayectoria x-y y orientación θ(t). |
| Entrega | Consolidar las evidencias y la documentación. | Informe de una página y tag `v1.0-rc0`. |

Estos criterios son metas del reto; todavía no representan resultados obtenidos por el equipo.

## Organización prevista del repositorio

La siguiente estructura es una propuesta de organización. Las carpetas y los archivos se incorporarán a medida que se desarrollen y verifiquen sus funciones.

| Ruta | Contenido previsto |
| --- | --- |
| `README.md` | Presentación del proyecto y guía general. |
| `config/wheel_params.yaml` | Parámetros de calibración utilizados por el sistema. |
| `capytown_esan/` | Código Python organizado por responsabilidad. |
| `capytown_esan/plot_odom.py` | Lectura del formato del bag desde `metadata.yaml` y generación de gráficas. |
| `launch/` | Archivos de arranque de los componentes necesarios. |
| `scripts/` | Herramientas auxiliares para preparar el entorno y ejecutar pruebas. |
| `docs/` | Procedimientos, predicciones y explicaciones técnicas. |
| `bags/` | Grabaciones de calibración y validación. |
| `plots/` | Gráficas generadas a partir de las grabaciones. |

Los registros `linea_recta.csv`, `calibration_log.csv`, `validacion.csv`, `setup_log.txt` y el archivo `informe.pdf` se incorporarán en la raíz según la consigna. Las grabaciones previstas son `bags/rc0_recta/`, `bags/rc0_giro/`, `bags/rc0_val_recta/` y `bags/rc0_val_giro/`.

Antes de implementar el código se revisará el paquete del laboratorio para mantener una estructura compatible con ROS 2 y aprovechar los componentes ya disponibles.

## Equipo y responsabilidades

El equipo de RC-0 está integrado por Sebastian, Karen, Anahi y Valentino, con los roles confirmados siguientes.

| Rol | Responsable | Responsabilidad en RC-0 |
| --- | --- | --- |
| Integración | Sebastian | Arranque, dominio, rosbag2, grabaciones y repositorio. |
| Control | Anahi | Calibración de `r` y `b_eff`, y actualización de parámetros. |
| Planificación | Valentino | Secuencias reproducibles de movimiento para las pruebas. |
| Percepción | Karen | Lectura de bags y generación de gráficas. |

**Grupo:** 7, **sección:** S-003, **ROS_DOMAIN_ID:** 20. **Radio:** `0.031584 m`. **b_eff por ensayo:** `0.27300 m` para 360° antihorario; `0.25500 m` para 360° horario; `0.27400 m` para el bonus antihorario de 720° (valor reportado por el equipo). El `wheel_params.yaml` de referencia conserva `0.27300 m`; los otros valores se aplicaron con `ros2 param set`. La rúbrica de Parte D exige mantener parámetros fijos: los resultados con cambios direccionales requieren esta aclaración.

## Criterios de desarrollo y documentación

Cada programa tendrá un propósito definido, instrucciones de ejecución y una explicación de las decisiones relevantes. Los parámetros ajustables incluirán sus unidades y se conservarán los registros de cada prueba.

El código, la configuración y las evidencias se organizarán por separado. Los cambios se registrarán con commits descriptivos para poder identificar qué se modificó y por qué.

## Material de referencia

- Consigna del curso: `RC0_Primer_Arranque_2026-2.docx`.
- Presentación del robot: `MicroROS-Pi5 (2).pptx`.

La documentación se actualizará con los comandos verificados en el laboratorio y las mediciones reales del equipo.



## Documentación final RC-0 (noviembre de 2026)

Consulta [`docs/rc0_entrega_grupo7.md`](docs/rc0_entrega_grupo7.md) para los roles, las tres configuraciones angulares, la validación A2, el historial de ensayos y las advertencias de la rúbrica. Los registros físicos y los rosbags se conservan en el paquete de entrega RC-0 del equipo.
