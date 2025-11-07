"""
JITX uses the `Pint <https://pint.readthedocs.io/en/stable/>`_ library for
units where applicable. Currently the support is limited, and primarily used for
component values, but will be expanded over time.

The unit registry and shorthand units are available here.
"""

import pint
from pint.facets.plain import PlainQuantity as PlainQuantity


registry = pint.UnitRegistry()
Quantity = registry.Quantity

mm = registry.mm
um = registry.um
nm = registry.nm
pm = registry.pm

# mil = registry.mil
# mils = registry.mils

percent = pct = registry.percent
ppm = registry.ppm

kV = registry.kV
V = registry.V
mV = registry.mV
uV = registry.uV

A = registry.A
mA = registry.mA
uA = registry.uA

mohm = registry.mohm
ohm = registry.ohm
kohm = registry.kohm
Mohm = registry.Mohm

F = registry.F
mF = registry.mF
uF = registry.uF
nF = registry.nF
pF = registry.pF

H = registry.H
mH = registry.mH
uH = registry.uH
nH = registry.nH

s = registry.s
ms = registry.ms
us = registry.us
ns = registry.ns
ps = registry.ps

Hz = registry.Hz
kHz = registry.kHz
MHz = registry.MHz
GHz = registry.GHz

dB = registry.dB
