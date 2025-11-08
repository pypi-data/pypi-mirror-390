"""
LEBSTA Units Library
====================

A Python library for unit definitions and conversions in engineering applications.

Usage:
    import lebsta_units as units
    
    force = 100 * units.kN
    pressure = 25 * units.MPa
"""

__version__ = "1.1.0"
__author__ = "LEBSTA"

# Unidades base
m = 1
kg = 1
s = 1

# Constantes Físicas
g = 9.8066 * m / s**2

# Unidades de masa
ton = 1000 * kg

# Unidades de dimension
cm = 0.01 * m
inch = 2.54 * cm
mm = 0.001 * m
ft = 0.3048 * m
km = 1000 * m

# Unidades de fuerza
kgf = kg * g
tonf = 1000 * kg * g
N = kg * m / s**2
kN = 1000 * N
kip = 1000 * N

# Unidades de Presión
Pa = N / m**2
kPa = 1000 * Pa
MPa = 10**6 * Pa
psi = 6894.76 * Pa
ksi = 1000 * psi

# Unidades de Tiempo
min = 60 * s
hr = 60 * min

# Lista de todas las unidades disponibles para importación
__all__ = [
    # Unidades base
    'm', 'kg', 's',
    # Constantes
    'g',
    # Masa
    'ton',
    # Dimensión
    'cm', 'inch', 'mm', 'ft', 'km',
    # Fuerza
    'kgf', 'tonf', 'N', 'kN', 'kip',
    # Presión
    'Pa', 'kPa', 'MPa', 'psi', 'ksi',
    # Tiempo
    'min', 'hr',
]
