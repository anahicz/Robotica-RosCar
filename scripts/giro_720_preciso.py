#!/usr/bin/env python3
"""RC-0 Grupo 7: giro de 720 grados y error frente a medicion fisica.

Basado en los controladores de giro originales del Grupo 7.
No cambia parametros de /odom_corrector. Guarda todos los intentos en un CSV.
Uso: python3 giro_720_preciso.py --sentido horario
     python3 giro_720_preciso.py --sentido antihorario
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

from giro_preciso_core import velocidad_control, cumple_bonus

OBJETIVO_GRADOS = 720.0
MAX_ANGULAR = 0.35  # rad/s; coincide con los scripts originales
MAX_TIME = 90.0
SALTO_MAX_GRADOS = 12.0
CSV_SALIDA = Path(__file__).resolve().parent / 'resultados_giro_720_preciso.csv'


class ControlGiro(Node):
    def __init__(self, sentido, factor=1.0, minima=0.04):
        super().__init__('rc0_giro_720_preciso')
        self.factor = factor  # grados físicos / grados de odometría; no modifica /odom
        self.minima = minima
        self.omega_medida = 0.0
        self.sentido = sentido
        self.signo = -1 if sentido == 'horario' else 1
        self.publicador = self.create_publisher(Twist, '/cmd_vel', 1)
        self.suscripcion = self.create_subscription(
            Odometry, '/odom', self.on_odom, 1
        )
        self.yaw_anterior = None
        self.ultimo_odom = 0.0
        self.giro_acumulado = 0.0  # radianes firmados
        self.midiendo = False
        self.alerta = None

    def on_odom(self, msg):
        q = msg.pose.pose.orientation
        valores = (q.x, q.y, q.z, q.w)
        norma = math.sqrt(sum(v*v for v in valores))
        if not math.isfinite(norma) or norma < 1e-9:
            self.alerta = 'Cuaternion de odometria no valido'
            return
        x, y, z, w = (v/norma for v in valores)
        yaw = math.atan2(
            2.0 * (w * z + x * y),
            1.0 - 2.0 * (y * y + z * z)
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
                dt = ahora - self.ultimo_odom
                if dt > 0:
                    self.omega_medida = 0.3 * delta/dt + 0.7 * self.omega_medida
        self.yaw_anterior = yaw
        self.ultimo_odom = ahora

    def mandar(self, velocidad=0.0):
        cmd = Twist()
        cmd.angular.z = float(velocidad)
        self.publicador.publish(cmd)

    def detener(self):
        # Mantener el seguimiento de /odom mientras se envian ceros,
        # para incluir el pequeno movimiento residual posterior a la parada.
        fin = time.monotonic() + 1.5
        proximo_cero = 0.0
        while rclpy.ok() and time.monotonic() < fin:
            ahora = time.monotonic()
            if ahora >= proximo_cero:
                self.mandar(0.0)
                proximo_cero = ahora + 0.05
            rclpy.spin_once(self, timeout_sec=0.02)
        self.mandar(0.0)

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
        proximo_control = 0.0
        proxima_impresion = 0.0
        ultimo_avance = inicio
        progreso_previo = 0.0
        self.omega_medida = 0.0
        try:
            print(f'Giro {self.sentido} hasta {OBJETIVO_GRADOS:.1f} grados estimados con factor {self.factor:.6f}')
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

                ahora = time.monotonic()
                if ahora < proximo_control:
                    continue
                proximo_control = ahora + 0.02
                progreso = self.signo * self.giro_acumulado
                progreso_fisico = math.degrees(progreso) * self.factor
                if progreso_fisico < -3.0:
                    motivo = 'sentido_inesperado'
                    break
                if progreso_fisico > progreso_previo + 0.1:
                    progreso_previo = progreso_fisico
                    ultimo_avance = ahora
                elif ahora - ultimo_avance > 4.0:
                    motivo = 'sin_avance'
                    print('\nNo hay avance medible: revisa velocidad minima/ruedas.')
                    break
                restante = OBJETIVO_GRADOS - progreso_fisico
                velocidad = velocidad_control(
                    restante, self.signo * self.omega_medida * self.factor,
                    maxima=MAX_ANGULAR, minima=self.minima)
                if velocidad == 0.0:
                    motivo = 'objetivo_alcanzado'
                    print('\nZona de parada: enviando ceros y midiendo movimiento residual')
                    break
                self.mandar(self.signo * velocidad)
                if ahora >= proxima_impresion:
                    print(f'\rGiro estimado: {progreso_fisico:.2f}° / {OBJETIVO_GRADOS:.1f}°',
                          end='', flush=True)
                    proxima_impresion = ahora + 0.2

        finally:
            al_ordenar_parada = math.degrees(self.giro_acumulado)
            self.detener()
            self.midiendo = False
            print('\nComandos de parada enviados.')

        if self.alerta or time.monotonic() - self.ultimo_odom > 0.6:
            print('ADVERTENCIA: /odom final no es fiable.')
            return None, motivo

        if abs(self.omega_medida * self.factor) > math.radians(0.5):
            print('ADVERTENCIA: /odom no acredita reposo al terminar.')
            return None, 'sin_reposo_confirmado'
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


def agregar_csv(sentido, real_grados, odom_firmado, error_pct, motivo, factor):
    nuevo = not CSV_SALIDA.exists() or CSV_SALIDA.stat().st_size == 0
    with CSV_SALIDA.open('a', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        if nuevo:
            writer.writerow([
                'fecha', 'prueba', 'sentido', 'objetivo_grados',
                'valor_real_grados', 'valor_odom_grados', 'error_%', 'error_objetivo_grados', 'bonus_cumple', 'estado', 'factor_real_por_odom', 'giro_estimado_grados'
            ])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bonus_giro_720', sentido, f'{OBJETIVO_GRADOS:.2f}',
            f'{real_grados:.2f}', f'{abs(odom_firmado):.2f}',
            f'{error_pct:.2f}', f'{abs(real_grados - OBJETIVO_GRADOS):.2f}',
            'SI' if cumple_bonus(real_grados, motivo, OBJETIVO_GRADOS) else 'NO',
            motivo, f'{factor:.8f}', f'{abs(odom_firmado)*factor:.2f}'
        ])
    print(f'Resultado agregado a: {CSV_SALIDA}')


def main():
    parser = argparse.ArgumentParser(description='Bonus RC-0: giro de 720 grados y calculo de errores')
    parser.add_argument('--sentido', choices=('horario', 'antihorario'), required=True)
    parser.add_argument('--factor', type=float, default=1.0,
                        help='giro fisico anterior / giro odom anterior, mismo sentido y superficie')
    parser.add_argument('--min-angular', type=float, default=0.04,
                        help='velocidad minima efectiva en rad/s (0.04 por defecto)')
    args = parser.parse_args()
    if not math.isfinite(args.factor) or not 0.5 <= args.factor <= 1.5:
        parser.error('--factor debe ser finito, entre 0.5 y 1.5; fuera de eso revisa la odometria')
    if not math.isfinite(args.min_angular) or not 0 < args.min_angular <= MAX_ANGULAR:
        parser.error('--min-angular debe ser positivo y no mayor que 0.35')

    print(f'Sentido seleccionado: {args.sentido}')
    print('Este script NO modifica wheel_radius ni wheel_separation.')
    print(f'Factor fisico/odom: {args.factor:.6f}; objetivo odom equivalente: {OBJETIVO_GRADOS/args.factor:.2f} grados')
    print('Verifica la calibracion activa, el espacio despejado y la parada accesible.')
    input('Con todo listo y supervisado, pulsa Enter para iniciar (Ctrl+C para cancelar): ')

    rclpy.init()
    nodo = ControlGiro(args.sentido, args.factor, args.min_angular)
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
    print(f'BONUS giro (error fisico < 5 grados): {"CUMPLE" if cumple_bonus(real, motivo, OBJETIVO_GRADOS) else "NO CUMPLE"}')
    print('NOTA: error odom-vs-fisico y error fisico-vs-objetivo son mediciones distintas.')
    if motivo != 'objetivo_alcanzado':
        print(f'ATENCION: corrida incompleta ({motivo}); no usar como validacion completa.')
    print('===========================================')
    agregar_csv(args.sentido, real, odom_final, error, motivo, args.factor)


if __name__ == '__main__':
    main()
