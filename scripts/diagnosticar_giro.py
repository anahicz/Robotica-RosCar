# =====================================================
# RC-0 / CapyTown - Grupo 7, seccion S-003
# Equipo responsable del repositorio:
# Sebastian Pedro Aguirre Acosta - Integracion
# Anahi Cortez Chinchay - Control
# Karen Noelia Ramirez Quevedo - Percepcion
# Valentino Uziel Vara Vargas - Planificacion
# Firma de documentacion; se respeta la autoria previa.
# =====================================================
import sys
import math
import rosbag2_py

from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw_deg(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.degrees(math.atan2(siny, cosy))


def diff_angle(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


if len(sys.argv) != 2:
    print("Uso: python3 diagnosticar_giro.py bags/NOMBRE_DEL_BAG")
    sys.exit(1)

ruta = sys.argv[1]

reader = rosbag2_py.SequentialReader()
reader.open(
    rosbag2_py.StorageOptions(uri=ruta, storage_id='sqlite3'),
    rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )
)

tipos = {
    item.name: get_message(item.type)
    for item in reader.get_all_topics_and_types()
}

datos = []

while reader.has_next():
    topic, raw, timestamp = reader.read_next()
    if topic not in ('/cmd_vel', '/odom', '/odom_raw'):
        continue
    msg = deserialize_message(raw, tipos[topic])
    datos.append((timestamp, topic, msg))

datos.sort(key=lambda x: x[0])

inicio = None
parada = None

for t, topic, msg in datos:
    if topic != '/cmd_vel':
        continue

    velocidad = msg.angular.z

    if inicio is None and abs(velocidad) > 0.01:
        inicio = t
    elif inicio is not None and parada is None and abs(velocidad) < 0.001:
        parada = t
        break

if inicio is None:
    print("No se encontraron comandos de giro en /cmd_vel.")
    sys.exit(1)

print(f"Inicio del giro: {inicio / 1e9:.3f} s")

if parada is None:
    print("No se encontró el primer comando de parada.")
else:
    print(f"Orden de parada: {parada / 1e9:.3f} s")
    print(f"Duración hasta parada: {(parada-inicio)/1e9:.3f} s")

for topic_buscado in ('/odom', '/odom_raw'):
    muestras = [
        (t, yaw_deg(msg.pose.pose.orientation))
        for t, topic, msg in datos
        if topic == topic_buscado and t >= inicio
    ]

    if len(muestras) < 2:
        print(f"\n{topic_buscado}: datos insuficientes")
        continue

    acumulado = 0.0
    giro_en_parada = None
    ultimo = muestras[0][1]

    for t, actual in muestras[1:]:
        acumulado += diff_angle(actual, ultimo)
        ultimo = actual

        if parada is not None and giro_en_parada is None and t >= parada:
            giro_en_parada = acumulado

    print(f"\n{topic_buscado}")
    print(f"Giro acumulado final: {acumulado:.2f}°")

    if giro_en_parada is not None:
        residual = acumulado - giro_en_parada
        print(f"Giro acumulado al parar: {giro_en_parada:.2f}°")
        print(f"Giro adicional registrado: {residual:.2f}°")