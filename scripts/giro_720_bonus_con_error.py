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
"""RC-0 Grupo 7: giro de 720 grados y error frente a medicion fisica.

Basado en los controladores de giro originales del Grupo 7.
No cambia parametros de /odom_corrector. Guarda todos los intentos en un CSV.
Uso: python3 giro_360_con_error.py --sentido horario
     python3 giro_360_con_error.py --sentido antihorario
"""

import argparse
import csv
import math
import time
from datetime import datetime
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

OBJETIVO_GRADOS = 720.0
MAX_ANGULAR = 0.35  # rad/s; coincide con los scripts originales
MAX_TIME = 90.0
SALTO_MAX_GRADOS = 12.0
CSV_SALIDA = Path(__file__).resolve().parent / 'resultados_bonus_720.csv'


class ControlGiro(Node):
    def __init__(self, sentido):
        super().__init__('rc0_giro_360_con_error')
        self.sentido = sentido
        self.signo = -1 if sentido == 'horario' else 1
        self.publicador = self.create_publisher(Twist, '/cmd_vel', 10)
        self.suscripcion = self.create_subscription(
            Odometry, '/odom', self.on_odom, 10
        )
        self.yaw_anterior = None
        self.ultimo_odom = 0.0
        self.giro_acumulado = 0.0  # radianes firmados
        self.midiendo = False
        self.alerta = None

    def on_odom(self, msg):
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )
        ahora = time.monotonic()
        if self.yaw_anterior is not None and self.midiendo:
            delta = math.atan2(
                math.sin(yaw - self.yaw_anterior),
                math.cos(yaw - self.yaw_anterior)
            )
            if abs(math.degrees(delta)) > SALTO_MAX_GRADOS:
                self.alerta = f'Salto de odometria: {math.degrees(delta):.1f} grados'
            else:
                self.giro_acumulado += delta
        self.yaw_anterior = yaw
        self.ultimo_odom = ahora

    def mandar(self, velocidad=0.0):
        cmd = Twist()
        cmd.angular.z = float(velocidad)
        self.publicador.publish(cmd)

    def detener(self):
        # Mantener el seguimiento de /odom mientras se envian ceros,
        # para incluir el pequeno movimiento residual posterior a la parada.
        for _ in range(20):
            self.mandar(0.0)
            if rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.075)

    def ejecutar(self):
        print('Esperando /odom reciente...')
        inicio_espera = time.monotonic()
        while rclpy.ok() and (
            self.yaw_anterior is None or time.monotonic() - self.ultimo_odom > 0.5
        ):
            rclpy.spin_once(self, timeout_sec=0.1)
            if time.monotonic() - inicio_espera > 6.0:
                raise RuntimeError('No hay /odom reciente; se cancela el giro')

        inicio_espera = time.monotonic()
        while rclpy.ok() and self.publicador.get_subscription_count() == 0:
            rclpy.spin_once(self, timeout_sec=0.1)
            if time.monotonic() - inicio_espera > 5.0:
                raise RuntimeError('No hay receptor de /cmd_vel; se cancela el giro')

        self.giro_acumulado = 0.0
        self.alerta = None
        inicio = time.monotonic()
        self.midiendo = True
        motivo = 'interrumpido'
        al_ordenar_parada = 0.0
        try:
            print(f'Giro {self.sentido} hasta {OBJETIVO_GRADOS:.1f} grados segun /odom')
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.02)
                if self.alerta:
                    motivo = 'salto_odom'
                    print('\nALERTA:', self.alerta)
                    break
                if time.monotonic() - inicio > MAX_TIME:
                    motivo = 'tiempo_limite'
                    print('\nTiempo limite: se ordena la parada')
                    break
                if time.monotonic() - self.ultimo_odom > 0.6:
                    motivo = 'odom_desactualizado'
                    print('\n/odom desactualizado: se ordena la parada')
                    break

                progreso = self.signo * self.giro_acumulado
                restante = math.radians(OBJETIVO_GRADOS) - progreso
                if restante <= 0:
                    motivo = 'objetivo_alcanzado'
                    print('\nObjetivo odometrico alcanzado')
                    break
                velocidad = min(MAX_ANGULAR, max(0.10, 0.6 * restante))
                self.mandar(self.signo * velocidad)
                print(f'\rProgreso /odom: {math.degrees(progreso):.2f}° / {OBJETIVO_GRADOS:.1f}°',
                      end='', flush=True)
                time.sleep(0.08)
        finally:
            al_ordenar_parada = math.degrees(self.giro_acumulado)
            self.detener()
            self.midiendo = False
            print('\nComandos de parada enviados.')

        if self.alerta or time.monotonic() - self.ultimo_odom > 0.6:
            print('ADVERTENCIA: /odom final no es fiable.')
            return None, motivo

        final_firmado = math.degrees(self.giro_acumulado)
        print(f'Giro /odom al ordenar parada: {al_ordenar_parada:+.2f}°')
        print(f'Giro /odom final:            {final_firmado:+.2f}°')
        print(f'Diferencia tras parada:      {final_firmado - al_ordenar_parada:+.2f}°')
        print(f'Motivo de finalizacion: {motivo}')
        return final_firmado, motivo


def pedir_angulo_fisico():
    print('\nCon el robot detenido, mide el giro fisico TOTAL, incluyendo vueltas completas.')
    while True:
        dato = input('Angulo fisico recorrido (grados positivos, Enter para omitir): ').strip()
        if not dato:
            return None
        try:
            grados = float(dato.replace(',', '.'))
            if not (math.isfinite(grados) and grados > 0):
                raise ValueError
            return grados
        except ValueError:
            print('Introduce un numero positivo. Ejemplo: 363 o 359,5.')


def agregar_csv(sentido, real_grados, odom_firmado, error_pct, motivo):
    nuevo = not CSV_SALIDA.exists() or CSV_SALIDA.stat().st_size == 0
    with CSV_SALIDA.open('a', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        if nuevo:
            writer.writerow([
                'fecha', 'prueba', 'sentido', 'objetivo_grados',
                'valor_real_grados', 'valor_odom_grados', 'error_%', 'error_objetivo_grados', 'bonus_cumple', 'estado'
            ])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bonus_giro_720', sentido, f'{OBJETIVO_GRADOS:.2f}',
            f'{real_grados:.2f}', f'{abs(odom_firmado):.2f}',
            f'{error_pct:.2f}', f'{abs(real_grados - OBJETIVO_GRADOS):.2f}',
            'SI' if abs(real_grados - OBJETIVO_GRADOS) <= 5.0 and motivo == 'objetivo_alcanzado' else 'NO',
            motivo
        ])
    print(f'Resultado agregado a: {CSV_SALIDA}')


def main():
    parser = argparse.ArgumentParser(description='Bonus RC-0: giro de 720 grados y calculo de errores')
    parser.add_argument('--sentido', choices=('horario', 'antihorario'), required=True)
    args = parser.parse_args()

    print(f'Sentido seleccionado: {args.sentido}')
    print('Este script NO modifica wheel_radius ni wheel_separation.')
    print('Verifica la calibracion activa, el espacio despejado y la parada accesible.')
    input('Con todo listo y supervisado, pulsa Enter para iniciar (Ctrl+C para cancelar): ')

    rclpy.init()
    nodo = ControlGiro(args.sentido)
    odom_final = None
    motivo = 'interrumpido'
    try:
        odom_final, motivo = nodo.ejecutar()
    except KeyboardInterrupt:
        print('\nMovimiento interrumpido por teclado.')
    except Exception as exc:
        print(f'Error: {exc}')
    finally:
        try:
            nodo.detener()
        finally:
            nodo.destroy_node()
            rclpy.shutdown()

    if odom_final is None:
        print('No se calcula el error: la corrida no dispone de odometria final fiable.')
        return

    real = pedir_angulo_fisico()
    if real is None:
        print('Medicion omitida; no se agregaron filas al CSV.')
        return
    odom = abs(odom_final)
    error = abs(odom - real) / real * 100.0
    diferencia = odom - real
    print('\n========== RESULTADO RC-0: GIRO ==========')
    print(f'Sentido:              {args.sentido}')
    print(f'Objetivo:             {OBJETIVO_GRADOS:.2f}°')
    print(f'Giro fisico:          {real:.2f}°')
    print(f'Giro /odom:           {odom:.2f}° (firmado: {odom_final:+.2f}°)')
    print(f'Diferencia odom-real: {diferencia:+.2f}°')
    print(f'ERROR RELATIVO:       {error:.2f} %')
    print(f'Error de giro fisico respecto a 720 grados: {abs(real - OBJETIVO_GRADOS):.2f} grados')
    print(f'BONUS giro (error fisico <= 5 grados): {"CUMPLE" if abs(real - OBJETIVO_GRADOS) <= 5.0 and motivo == "objetivo_alcanzado" else "NO CUMPLE"}')
    print('NOTA: error odom-vs-fisico y error fisico-vs-objetivo son mediciones distintas.')
    if motivo != 'objetivo_alcanzado':
        print(f'ATENCION: corrida incompleta ({motivo}); no usar como validacion completa.')
    print('===========================================')
    agregar_csv(args.sentido, real, odom_final, error, motivo)


if __name__ == '__main__':
    main()
