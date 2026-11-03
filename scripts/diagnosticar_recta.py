import math
import sys

from rosbag2_py import (
    SequentialReader,
    StorageOptions,
    ConverterOptions
)
from rclpy.serialization import deserialize_message
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def diagnosticar(ruta):
    reader = SequentialReader()

    reader.open(
        StorageOptions(uri=ruta, storage_id="sqlite3"),
        ConverterOptions("", "")
    )

    comandos = []
    odometria = {"/odom": [], "/odom_raw": []}

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic == "/cmd_vel":
            msg = deserialize_message(data, Twist)
            comandos.append((
                timestamp,
                msg.linear.x,
                msg.angular.z
            ))

        elif topic in odometria:
            msg = deserialize_message(data, Odometry)
            p = msg.pose.pose.position
            q = msg.pose.pose.orientation

            theta = math.atan2(
                2 * (q.w * q.z + q.x * q.y),
                1 - 2 * (q.y*q.y + q.z*q.z)
            )

            odometria[topic].append(
                (timestamp, p.x, p.y, theta)
            )

    if not comandos:
        print("ERROR: El bag no contiene comandos.")
        return

    activos = [
        (t, v, w) for t, v, w in comandos
        if abs(v) > 0.001 or abs(w) > 0.001
    ]

    print("\n=== DIAGNOSTICO RC-0 ===")
    print(f"Mensajes /cmd_vel: {len(comandos)}")
    print(f"Comandos activos: {len(activos)}")
    print(f"Comandos de parada: {len(comandos)-len(activos)}")

    print("\nPrimeros 5 comandos:")
    for t, v, w in comandos[:5]:
        print(f"v={v:.3f}, w={w:.3f}")

    print("\nÚltimos 8 comandos:")
    for t, v, w in comandos[-8:]:
        print(f"v={v:.3f}, w={w:.3f}")

    if not activos:
        print("No se encontraron comandos de movimiento.")
        return

    inicio = activos[0][0]
    ultimo_activo = activos[-1][0]

    paradas = [
        t for t, v, w in comandos
        if t > ultimo_activo
        and abs(v) <= 0.001
        and abs(w) <= 0.001
    ]

    fin = paradas[0] if paradas else ultimo_activo
    fin_movimiento = fin + int(1.0 * 1e9)

    print(f"\nDuración entre comandos: {(fin-inicio)/1e9:.3f} s")
    print(f"Orden de parada posterior: {'Sí' if paradas else 'No'}")

    for topic, datos in odometria.items():
        tramo = [
            item for item in datos
            if inicio <= item[0] <= fin_movimiento
        ]

        if len(tramo) < 2:
            print(f"\n{topic}: datos insuficientes")
            continue

        _, x0, y0, theta0 = tramo[0]
        _, xf, yf, thetaf = tramo[-1]

        dx = xf - x0
        dy = yf - y0

        avance = (
            dx * math.cos(theta0)
            + dy * math.sin(theta0)
        )

        lateral = (
            -dx * math.sin(theta0)
            + dy * math.cos(theta0)
        )

        distancia = math.hypot(dx, dy)

        error = abs(1.0 - distancia) * 100

        print(f"\n=== {topic} ===")
        print(f"Muestras: {len(tramo)}")
        print(f"Orientación inicial: {math.degrees(theta0):.2f}°")
        print(f"Orientación final: {math.degrees(thetaf):.2f}°")
        print(f"Avance longitudinal: {avance:.4f} m")
        print(f"Desplazamiento lateral: {lateral:.4f} m")
        print(f"Distancia entre extremos: {distancia:.4f} m")
        print(f"Error respecto a 1 m: {error:.2f}%")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 diagnosticar_recta.py RUTA_BAG")
        sys.exit(1)

    diagnosticar(sys.argv[1])
