from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.layerindex import Side
from jitx.net import Net, Port
from jitx.constraints import ViaFencePattern
from jitx.shapes.composites import rectangle
from jitx.si import Constrain, ReferencePlanes, RoutingStructure
from jitx.symbol import Symbol, Pin, Direction, SymbolOrientation
from jitx.sample import (
    SampleDesign,
    SampleSubstrate,
)
from jitx.feature import KeepOut, Soldermask, Courtyard

from jitx.test import TestCase
from jitx.units import ohm
from jitx.via import Via, ViaType


class ConstraintVia(Via):
    start_layer = 0
    stop_layer = -1
    diameter = 0.45
    hole_diameter = 0.3
    type = ViaType.MechanicalDrill


class ConstraintPad(Pad):
    shape = rectangle(0.75, 0.75)
    soldermask = Soldermask(shape)


class ConstraintLandpattern(Landpattern):
    pad1 = ConstraintPad().at(-0.5, 0)
    pad2 = ConstraintPad().at(0.5, 0)
    courtyard = Courtyard(rectangle(2, 1))


class ConstraintSymbol(Symbol):
    pin1 = Pin(at=(-1, 0), length=1, direction=Direction.Left)
    pin2 = Pin(at=(1, 0), length=1, direction=Direction.Right)
    draw = rectangle(2, 1)
    orientation = SymbolOrientation(0)


class ConstraintComponent(Component):
    landpattern = ConstraintLandpattern()
    symbol = ConstraintSymbol()
    p = {
        1: Port(),
        2: Port(),
    }


RS_37 = RoutingStructure(
    impedance=37 * ohm,
    layers={
        0: RoutingStructure.Layer(
            trace_width=0.3,
            velocity=3.0,
            insertion_loss=0.05,
        )
        .geometry(Soldermask, width=0.65, side=Side.Top)
        .geometry(KeepOut, width=1.5, layers=1, pour=True)
        .reference(0, desired_width=8)
        .reference(1, desired_width=6)
        .fence(
            SampleSubstrate.THVia,
            ViaFencePattern(pitch=1.0, offset=1.0, num_rows=4),
        ),
        1: RoutingStructure.Layer(trace_width=0.3, velocity=3.0, insertion_loss=0.05),
    },
)


class ConstraintCircuit(Circuit):
    def __init__(self):
        self.c = [ConstraintComponent() for _ in range(2)]
        self.GND = self.c[0].p[2] + self.c[1].p[2]
        # with ReferencePlanes({0: self.GND, 1: self.GND}):
        self += self.c[0].p[1] >> self.c[1].p[1]
        self.constraint = Constrain(self.c[0].p[1].to(self.c[1].p[1])).structure(RS_37)


class ConstraintMain(Circuit):
    gnd = Net(name="gnd")
    planes = ReferencePlanes({0: gnd, 1: gnd})

    A = Port()
    B = Port()

    gnd += A + B

    def __init__(self):
        self.c = ConstraintCircuit()
        self.gnd += self.c.c[0].p[2]
        # self.gnd += self.c.GND


class ConstraintDesign(SampleDesign):
    circuit = ConstraintMain()


class ConstraintTest(TestCase):
    def test_constraint(self):
        design = ConstraintDesign()
        self.assertIsInstance(design.circuit, ConstraintMain)
