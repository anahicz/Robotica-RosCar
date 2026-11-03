#!/usr/bin/env python3
"""Parte E (RC-0): dos gráficos por bag de /odom, compatible con sqlite3 y mcap."""
import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry


def leer_pose(bag: Path, topic: str):
    metadata_path = bag / 'metadata.yaml'
    if not metadata_path.is_file():
        raise FileNotFoundError(f'No se encuentra {metadata_path}')
    with metadata_path.open('r', encoding='utf-8') as f:
        metadata = yaml.safe_load(f)['rosbag2_bagfile_information']
    formato = metadata['storage_identifier']
    if formato not in ('sqlite3', 'mcap'):
        raise ValueError(f'Formato no admitido: {formato}')

    lector = SequentialReader()
    lector.open(StorageOptions(uri=str(bag), storage_id=formato),
                ConverterOptions(input_serialization_format='cdr', output_serialization_format='cdr'))
    t, x, y, theta = [], [], [], []
    while lector.has_next():
        nombre, datos, marca = lector.read_next()
        if nombre != topic:
            continue
        msg = deserialize_message(datos, Odometry)
        q = msg.pose.pose.orientation
        angulo = math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2 * (q.y*q.y + q.z*q.z))
        t.append(marca * 1e-9)
        x.append(msg.pose.pose.position.x)
        y.append(msg.pose.pose.position.y)
        theta.append(angulo)
    if not t:
        raise ValueError(f'El bag {bag} no contiene mensajes del tópico {topic}')
    return t, x, y, theta, formato


def guardar_graficas(bag: Path, salida: Path, topic: str):
    t, x, y, angulos, formato = leer_pose(bag, topic)
    salida.mkdir(parents=True, exist_ok=True)
    prefijo = bag.name + ('' if topic == '/odom' else '_' + topic.strip('/').replace('/', '_'))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(x, y, lw=1.6, color='#245A81', label='Trayectoria /odom')
    ax.scatter([x[0]], [y[0]], color='green', marker='o', s=45, label='Inicio', zorder=5)
    ax.scatter([x[-1]], [y[-1]], color='red', marker='x', s=55, label='Fin', zorder=5)
    ax.set_xlabel('Posición X (m)')
    ax.set_ylabel('Posición Y (m)')
    ax.set_title(f'Trayectoria X-Y — {bag.name}')
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    fig.tight_layout()
    xy = salida / f'{prefijo}_xy.png'
    fig.savefig(xy, dpi=160)
    plt.close(fig)

    # Desenvolver atan2 para evitar saltos ficticios de +/-180 grados.
    theta_acum = [0.0]
    for anterior, actual in zip(angulos, angulos[1:]):
        delta = math.atan2(math.sin(actual-anterior), math.cos(actual-anterior))
        theta_acum.append(theta_acum[-1] + math.degrees(delta))
    tiempos = [instante - t[0] for instante in t]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(tiempos, theta_acum, lw=1.6, color='#9B4F74')
    ax.scatter([tiempos[-1]], [theta_acum[-1]], color='red', s=35, zorder=4)
    ax.set_xlabel('Tiempo desde inicio del bag (s)')
    ax.set_ylabel('Orientación acumulada relativa (grados)')
    ax.set_title(f'Orientación θ(t) — {bag.name}')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    th = salida / f'{prefijo}_theta_t.png'
    fig.savefig(th, dpi=160)
    plt.close(fig)
    print(f'Bag: {bag}  |  almacenamiento: {formato}  |  muestras: {len(t)}')
    print(f'Ángulo acumulado relativo: {theta_acum[-1]:.2f}°')
    print(f'PNG X-Y: {xy}')
    print(f'PNG θ(t): {th}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parte E: gráficas de /odom desde un rosbag ROS 2')
    parser.add_argument('bag', help='Carpeta del rosbag con metadata.yaml')
    parser.add_argument('--out', default='plots', help='Carpeta de salida (predeterminado: plots)')
    parser.add_argument('--topic', default='/odom', help='Tópico odométrico (predeterminado: /odom)')
    args = parser.parse_args()
    guardar_graficas(Path(args.bag), Path(args.out), args.topic)
