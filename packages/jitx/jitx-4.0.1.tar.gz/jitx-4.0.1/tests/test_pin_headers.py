from jitx.board import Board
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.constraints import BinaryDesignConstraint as BinaryDesignRule, Tag
from jitx.container import Composite
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.layerindex import Side
from jitx.net import Port
from jitx.symbol import Symbol, SymbolMapping, Pin, Direction
from jitx.design import Design
from jitx.shapes.primitive import Polygon
from jitx.substrate import FabricationConstraints, Substrate
from jitx.stackup import Conductor, Dielectric, Stackup
from jitx.feature import Soldermask

import jitx.test
from jitx.via import Via, ViaType
from jitx.transform import Transform
from jitx.shapes import Shape
from jitx.landpattern import PadShape


# TODO: Make this a Pad method?
def pad_shape(p: Pad) -> Shape:
    if isinstance(p.shape, PadShape):
        return p.shape.shape
    else:
        return p.shape


class CopperConductor(Conductor):
    pass


class MyStackup(Stackup):
    layers = [
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1),
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1),
        Dielectric(thickness=0.1),
    ]


class MyFabConstraints(FabricationConstraints):
    min_copper_width = 0.127
    min_copper_copper_space = 0.127
    min_copper_hole_space = 0.127
    min_copper_edge_space = 0.127

    min_annular_ring = 0.127
    min_drill_diameter = 0.127
    min_silkscreen_width = 0.127
    min_pitch_leaded = 0.127
    min_pitch_bga = 0.127

    max_board_width = 0.127
    max_board_height = 0.127

    min_silk_solder_mask_space = 0.127
    min_silkscreen_text_height = 0.127
    solder_mask_registration = 0.127
    min_soldermask_opening = 0.127
    min_soldermask_bridge = 0.127

    min_th_pad_expand_outer = 0.127
    min_hole_to_hole = 0.127
    min_pth_pin_solder_clearance = 0.127


class MyVia(Via):
    start_layer = 0
    stop_layer = 1
    diameter = 0.3
    hole_diameter = 0.1
    filled = True
    tented = Side.Top
    type = ViaType.LaserDrill


class MySubstrate(Substrate):
    stackup = MyStackup()
    constraints = MyFabConstraints()
    vias = [MyVia]


class MyBoard(Board):
    # Create a rectangular board that's large enough for our resistor circuit
    shape = Polygon(
        [
            (-10, -5),  # bottom left
            (10, -5),  # bottom right
            (10, 5),  # top right
            (-10, 5),  # top left
        ]
    )


class MyPad(Pad):
    shape = Polygon([(-0.2, 0.2), (0.2, 0.2), (0.2, -0.2), (-0.2, -0.2)])

    def __init__(self):
        self.soldermask = Soldermask(pad_shape(self))


class MyLandpattern(Landpattern):
    def __init__(self, n: int):
        self.sub = Composite(Transform.rotate(45))
        self.pads = []
        for i in range(n):
            self.pads.append(MyPad().at(i, 0))


class MySymbol(Symbol):
    def __init__(self, n: int):
        self.pins = []
        for i in range(n):
            self.pins.append(Pin(at=(2, i), length=1, direction=Direction.Right))


class MyComponent(Component):
    def __init__(self, n: int):
        self.lp = MyLandpattern(n)
        self.sym = MySymbol(n)
        self.p = [Port() for _ in range(n)]
        self.mappings = [
            SymbolMapping({self.p[i]: self.sym.pins[i] for i in range(n)}),
            PadMapping({self.p[i]: self.lp.pads[i] for i in range(n)}),
        ]


class MyCircuit(Circuit):
    def __init__(self, n: int):
        self.cs = [MyComponent(n), MyComponent(n)]

        # Connect resistors in series
        self.nets = [self.cs[0].p[i] + self.cs[1].p[i] for i in range(n)]


class DP_1(Tag):
    pass


class DP_2(Tag):
    pass


class DP_3(Tag):
    pass


class DP_4(Tag):
    pass


class DP_5(Tag):
    pass


class DP_6(Tag):
    pass


class MyDesign(Design):
    board = MyBoard()
    substrate = MySubstrate()

    def __init__(self):
        self.circuit = MyCircuit(3)
        for tag, net in zip([DP_1(), DP_2(), DP_3()], self.circuit.nets, strict=False):
            tag.assign(net)
        self.rules = []
        self.rules.append(BinaryDesignRule(DP_1(), DP_2() | DP_3()).clearance(0.2))
        self.rules.append(BinaryDesignRule(DP_2(), DP_1() | DP_3()).clearance(0.2))
        self.rules.append(BinaryDesignRule(DP_3(), DP_1() | DP_2()).clearance(0.2))


class MyTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = MyDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
