# Arranque de RC-0 en el carro del equipo

Esta version incorpora un paquete propio `capytown_esan` para la instalacion observada en el laboratorio. El carro publica odometria en `/odom_raw`, mientras que la consigna utiliza `/odom` y pide grabar `/tf`. El adaptador publica la misma medicion en `/odom` y representa su pose como una transformacion TF.

El contenedor `micro_ros_agent` ya esta activo y la placa aparece como `/YB_Car_Node`. Este `bringup.launch.py` arranca solamente el adaptador: a diferencia del bringup descrito en la consigna, utiliza el agente que ya esta ejecutandose por separado. Esta diferencia debe quedar explicada en la entrega.

## Ubicacion de los archivos

| Entorno | Carpeta del repositorio |
| --- | --- |
| Windows | Carpeta clonada o actualizada del proyecto |
| Linux remoto del carro, fuera de Docker | `/home/pi/yahboomcar_ws/src/Robotica-RosCar` |
| Docker `ros2_dev` | `/root/yahboomcar_ws/src/Robotica-RosCar` |

Las dos rutas Linux muestran los mismos archivos mediante el montaje compartido confirmado en Docker. Transfiere los archivos del paquete desde Windows con WinSCP hacia la carpeta del repositorio del carro. La carpeta que contiene `package.xml` tambien debe contener `setup.py`, `setup.cfg` y la carpeta Python `capytown_esan`.

## Compilacion

En una terminal del Linux remoto fuera de Docker:

```bash
docker exec -it ros2_dev bash
```

Dentro de Docker:

```bash
cd /root/yahboomcar_ws/src/Robotica-RosCar
bash scripts/build_rc0.sh
```

El script utiliza exclusivamente el paquete de este repositorio. Guarda los resultados en `build_rc0`, `install_rc0` y `log_rc0`, dentro de `/root/yahboomcar_ws`. Esas carpetas estan en el montaje persistente y fuera del repositorio.

Este paso utiliza las dependencias ROS ya instaladas en el contenedor. Si falta alguna, conserva el error exacto para revisar esa dependencia antes de continuar. El script no realiza descargas.

## Ejecucion

En la terminal de Docker donde termino la compilacion:

```bash
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install_rc0/setup.bash
export ROS_DOMAIN_ID=20
ros2 launch capytown_esan bringup.launch.py
```

El dominio 20 es el valor observado en la terminal del carro. Aun falta confirmar el numero del grupo y la configuracion del firmware para verificar el requisito de aislamiento de la consigna.

Al recibir datos debe aparecer un mensaje similar a:

```text
Primera odometria recibida. Marcos: odom_frame -> base_footprint.
```

Los nombres de los marcos se toman del mensaje original. En las capturas del equipo eran `odom_frame` y `base_footprint`; el nombre del topico `/odom` no obliga a que el marco se llame igual.

Este lanzamiento no publica ordenes de movimiento. Deja abierta la terminal mientras verificas los datos. Ctrl+C cierra el adaptador.

## Verificacion en el carro

Abre otra terminal fuera de Docker y entra al contenedor:

```bash
docker exec -it ros2_dev bash
```

En esa nueva terminal de Docker:

```bash
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install_rc0/setup.bash
export ROS_DOMAIN_ID=20
ros2 topic list
ros2 topic echo /odom --once
ros2 topic echo /tf --once
```

Debe mantenerse `/odom_raw` y aparecer `/odom` y `/tf`. En `/tf` deben coincidir el marco padre y el hijo con los campos `header.frame_id` y `child_frame_id` de `/odom`. La posicion y la orientacion de cada transformacion se copian de la misma medicion de origen. Los mensajes leidos por separado no tienen por que corresponder exactamente al mismo instante.

La verificacion real sigue pendiente hasta ejecutar estos pasos en ROS 2 Humble del carro. Las comprobaciones de sintaxis y empaquetado realizadas durante la preparacion no sustituyen esta prueba.

## Explicacion del codigo

| Archivo | Funcion |
| --- | --- |
| `capytown_esan/odom_adapter.py` | Recibe la odometria nativa, comprueba la pose y publica `/odom` y su TF. |
| `config/odom_adapter.yaml` | Configura el topico de entrada, el de salida y la publicacion de TF. |
| `launch/bringup.launch.py` | Arranca el adaptador con la configuracion instalada. |
| `package.xml` | Declara el nombre del paquete, su tipo y dependencias de ROS 2. |
| `setup.py` y `setup.cfg` | Registran el ejecutable Python y los recursos del paquete. |
| `resource/capytown_esan` | Permite que el indice de paquetes de ROS 2 encuentre el proyecto. |
| `scripts/build_rc0.sh` | Compila este paquete en carpetas especificas de RC-0. |
| `setup_log.txt` | Registra las comprobaciones observadas y lo que todavia falta verificar. |

El adaptador se suscribe con el perfil de sensores best effort para ser compatible con la publicacion de la placa. Publica la salida de odometria con la configuracion reliable predeterminada de ROS 2. Los receptores best effort pueden recibir de un emisor reliable; un receptor reliable no puede exigir esa garantia a un emisor best effort.

Para TF se utilizan dos marcos: el origen de la odometria y el marco del robot. La transformacion indica donde se encuentra el robot respecto al origen, con la posicion y el cuaternion que ya proporciona la placa. Se conserva el tiempo original de la medicion.

Los mensajes con marcos vacios o iguales, valores no finitos o cuaterniones claramente no unitarios se descartan con una advertencia. El adaptador tampoco permite que entrada y salida resuelvan al mismo topico, porque eso provocaria un bucle de republicacion.

Esta adaptacion no aplica factores de escala, no calibra las ruedas y no fusiona la IMU. `config/odom_adapter.yaml` configura la comunicacion; los parametros fisicos `r` y `b_eff` se incorporaran cuando revisemos como se aplican realmente al modelo del carro.

## Evidencias pendientes de Parte A

- Confirmar numero de grupo, dominio en placa y aislamiento respecto a otros equipos.
- Verificar el adaptador en el carro y registrar la frecuencia de `/odom`.
- Guardar las salidas completas de frecuencias en texto junto a `setup_log.txt`.
- Actualizar la captura de rqt_graph con el adaptador y sus conexiones.
- Comprobar los plugins sqlite3 y mcap antes de grabar las corridas oficiales.
- Completar integrantes, roles y licencia del codigo en los metadatos que correspondan.

## Referencias tecnicas

- [ROS 2 Humble Creating a package](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html)
- [ROS 2 Humble Writing a broadcaster Python](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Broadcaster-Py.html)
- [ROS 2 Humble QoS compatibility](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [colcon Build arguments](https://colcon.readthedocs.io/en/released/reference/verb/build.html)
- [colcon Discovery arguments](https://colcon.readthedocs.io/en/released/reference/discovery-arguments.html)
- [Yahboom MicroROS-Pi5 Robot state estimation](https://www.yahboom.net/study/MicroROS-Pi5/10627/)
