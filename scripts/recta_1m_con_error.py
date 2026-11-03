#!/usr/bin/env python3
# =====================================================
# RC-0 / CapyTown - Grupo 7, seccion S-003
# Equipo responsable del repositorio:
# Sebastian Pedro Aguirre Acosta - Integracion
# Anahi Cortez Chinchay - Control
# Karen Noelia Ramirez Quevedo - Percepcion
# Valentino Uziel Vara Vargas - Planificacion
# Firma de documentacion; se respeta la autoria previa.
# =====================================================
"""RC-0 Grupo 7: recta 1 m con medición física posterior y cálculo de error.
Basado en recta_1m.py del proyecto; no modifica calibración ni parámetros ROS.
"""
import csv
import math
import time
from datetime import datetime
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

OBJETIVO_M = 1.0
CSV_SALIDA = Path(__file__).resolve().parent / 'resultados_recta_con_error.csv'


class Control(Node):
    def __init__(self):
        super().__init__('rc0_recta_1m_con_error')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(Odometry, '/odom', self.odometria, 10)
        self.pose = None
        self.ultima_lectura = 0.0

    def odometria(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z)
        )
        self.pose = (p.x, p.y, yaw)
        self.ultima_lectura = time.monotonic()

    def mandar(self, velocidad=0.0):
        cmd = Twist()
        cmd.linear.x = float(velocidad)
        self.pub.publish(cmd)

    def progreso_desde(self, origen):
        x0, y0, yaw0 = origen
        x, y, _ = self.pose
        return (x - x0) * math.cos(yaw0) + (y - y0) * math.sin(yaw0)

    def parar(self):
        # Publica ceros durante 1,5 s y sigue procesando /odom
        for _ in range(15):
            self.mandar(0.0)
            rclpy.spin_once(self, timeout_sec=0.1)

    def ejecutar(self):
        print('Esperando /odom reciente...')
        espera = time.monotonic()
        while rclpy.ok() and (self.pose is None or time.monotonic() - self.ultima_lectura > 0.5):
            rclpy.spin_once(self, timeout_sec=0.1)
            if time.monotonic() - espera > 6.0:
                raise RuntimeError('No llega /odom actualizado; movimiento cancelado')

        if self.pub.get_subscription_count() == 0:
            raise RuntimeError('Ningún suscriptor de /cmd_vel; movimiento cancelado')

        origen = self.pose
        inicio = time.monotonic()
        motivo = 'interrumpido'
        print('Avance recto hacia 1.000 m según /odom')
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.02)
                if time.monotonic() - inicio > 40.0:
                    motivo = 'tiempo_limite'
                    print('\nTiempo límite: parada de seguridad')
                    break
                if time.monotonic() - self.ultima_lectura > 0.6:
                    motivo = 'odom_desactualizado'
                    print('\n/odom desactualizado: parada de seguridad')
                    break
                progreso = self.progreso_desde(origen)
                restante = OBJETIVO_M - progreso
                if restante <= 0:
                    motivo = 'objetivo_alcanzado'
                    print('\nObjetivo odométrico alcanzado')
                    break
                velocidad = min(0.10, max(0.025, 0.8 * restante))
                self.mandar(velocidad)
                print(f'\rProgreso /odom: {progreso:.3f} / {OBJETIVO_M:.3f} m', end='', flush=True)
                time.sleep(0.08)
        finally:
            self.parar()
            print('\nRobot detenido (comandos de parada enviados).')

        # Se mide al FINAL, después de enviar comandos de parada.
        if time.monotonic() - self.ultima_lectura > 0.6:
            print('ADVERTENCIA: /odom final no está actualizado.')
            return None, 'odom_final_desactualizado'
        odom_final = self.progreso_desde(origen)
        print(f'Distancia longitudinal FINAL según /odom: {odom_final:.4f} m ({odom_final*100:.2f} cm)')
        print(f'Motivo de finalización: {motivo}')
        return odom_final, motivo


def pedir_distancia_fisica():
    print('\nMide con cinta la distancia física REAL entre inicio y fin.')
    while True:
        dato = input('Distancia física recorrida (en CENTÍMETROS; Enter para omitir): ').strip()
        if not dato:
            return None
        try:
            cm = float(dato.replace(',', '.'))
            if not (math.isfinite(cm) and cm > 0):
                raise ValueError
            return cm / 100.0
        except ValueError:
            print('Introduce un número positivo; por ejemplo 95.2 o 99,8.')


def guardar_csv(odom_m, fisica_m, error_pct, motivo):
    nuevo = not CSV_SALIDA.exists() or CSV_SALIDA.stat().st_size == 0
    with CSV_SALIDA.open('a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if nuevo:
            writer.writerow(['fecha', 'prueba', 'objetivo_m', 'valor_real_m', 'valor_odom_m', 'error_%', 'estado'])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'recta_1m',
            f'{OBJETIVO_M:.3f}', f'{fisica_m:.4f}', f'{odom_m:.4f}',
            f'{error_pct:.2f}', motivo
        ])
    print(f'Resultado añadido a: {CSV_SALIDA}')


def main():
    rclpy.init()
    node = Control()
    odom_final = None
    motivo = 'interrumpido'
    try:
        odom_final, motivo = node.ejecutar()
    except KeyboardInterrupt:
        print('\nInterrupción por teclado; movimiento cancelado.')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        node.parar()
        node.destroy_node()
        rclpy.shutdown()

    if odom_final is None:
        print('No se calcula error porque faltó una lectura final fiable.')
        return
    fisica_m = pedir_distancia_fisica()
    if fisica_m is None:
        print('Medición omitida; no se modificó el CSV.')
        return
    error = abs(odom_final - fisica_m) / fisica_m * 100.0
    print('\n========== RESULTADO RC-0 ==========')
    print(f'Objetivo:           {OBJETIVO_M:.3f} m')
    print(f'Distancia física:   {fisica_m:.4f} m ({fisica_m*100:.2f} cm)')
    print(f'Distancia /odom:    {odom_final:.4f} m ({odom_final*100:.2f} cm)')
    print(f'Diferencia:         {abs(odom_final - fisica_m)*100:.2f} cm')
    print(f'ERROR RELATIVO:     {error:.2f} %')
    print(f'Referencia ≤ 2 %:   {"CUMPLE" if error <= 2 else "NO CUMPLE"}')
    if motivo != 'objetivo_alcanzado':
        print(f'ATENCIÓN: corrida incompleta ({motivo}); revisar antes de usar como validación.')
    print('====================================')
    guardar_csv(odom_final, fisica_m, error, motivo)


if __name__ == '__main__':
    main()
