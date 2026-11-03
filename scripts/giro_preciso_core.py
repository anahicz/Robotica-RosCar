"""Cálculo puro. El error físico requiere una medición externa al robot."""
import math


def factor_calibracion(real_grados, odom_grados):
    if not all(math.isfinite(x) and x > 0 for x in (real_grados, odom_grados)):
        raise ValueError('Mediciones de calibración positivas y finitas requeridas')
    return real_grados / odom_grados


def velocidad_control(restante_grados, velocidad_medida_rad_s=0.0,
                      maxima=0.35, minima=0.04, tolerancia_grados=0.7,
                      anticipacion_s=0.12):
    values = (restante_grados, velocidad_medida_rad_s, maxima, minima,
              tolerancia_grados, anticipacion_s)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Medición o parámetro no finito')
    if not (0 < minima <= maxima <= 0.35 and 0 < tolerancia_grados < 5
            and 0 <= anticipacion_s <= 1):
        raise ValueError('Parámetros de control fuera de rango')
    # Sólo predice el movimiento hacia el objetivo; nunca ordena un giro inverso.
    avance_residual = math.degrees(max(0.0, velocidad_medida_rad_s)) * anticipacion_s
    if restante_grados <= tolerancia_grados + avance_residual:
        return 0.0
    # Tres zonas: una velocidad de crucero, una intermedia y una final.
    limite = maxima if restante_grados > 30 else min(maxima, 0.12)
    if restante_grados <= 8:
        limite = min(maxima, max(minima, 0.06))
    return min(limite, max(minima, 0.6 * math.radians(restante_grados)))


def cumple_bonus(real_grados, motivo, objetivo=720.0):
    return (math.isfinite(real_grados) and real_grados > 0
            and abs(real_grados - objetivo) < 5.0
            and motivo == 'objetivo_alcanzado')
