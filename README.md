# Robotica-RosCar

Proyecto académico de Robótica de la Universidad ESAN, desarrollado con el robot **MicroROS-Pi5 Robot Car** dentro del proyecto **CapyTown**.

Este repositorio reunirá el código, las configuraciones, la documentación y las evidencias de las pruebas realizadas durante el curso. El trabajo se desarrollará mediante conexión remota al entorno Linux de la Raspberry Pi 5 y el uso de ROS 2 Humble en Docker.

**Etapa actual:** RC-0 — Primer arranque y calibración del robot.  
**Periodo académico:** 2026-2.  
**Sección:** S-003.  
**Estado:** paquete de Parte A preparado; instalación y verificación en el carro pendientes.

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

El reto establece cuatro integrantes, uno por rol. Los nombres y las asignaciones están pendientes de completar.

| Rol | Responsabilidad en RC-0 |
| --- | --- |
| Integración | Arranque, dominio, rosbag2, grabaciones y repositorio. |
| Control | Calibración de `r` y `b_eff`, y actualización de parámetros. |
| Planificación | Secuencias reproducibles de movimiento para las pruebas. |
| Percepción | Lectura de bags y generación de gráficas. |

También se registrarán el número de grupo, su `ROS_DOMAIN_ID` y los valores finales de `r` y `b_eff`.

## Criterios de desarrollo y documentación

Cada programa tendrá un propósito definido, instrucciones de ejecución y una explicación de las decisiones relevantes. Los parámetros ajustables incluirán sus unidades y se conservarán los registros de cada prueba.

El código, la configuración y las evidencias se organizarán por separado. Los cambios se registrarán con commits descriptivos para poder identificar qué se modificó y por qué.

## Material de referencia

- Consigna del curso: `RC0_Primer_Arranque_2026-2.docx`.
- Presentación del robot: `MicroROS-Pi5 (2).pptx`.

La documentación se actualizará con los comandos verificados en el laboratorio y las mediciones reales del equipo.

