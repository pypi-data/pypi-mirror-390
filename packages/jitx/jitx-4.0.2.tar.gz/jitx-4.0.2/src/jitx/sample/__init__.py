"""The sample package contains sample classes of common base design elements,
primarily useful for creating test cases, and can be used when
experimenting without wanting to select a stackup or fabrication rules. The
implementations in here do not reflect any real world applications, and may be
changed at any time without notice, and thus should not be relied upon when
creating actual designs.

>>> class MyPlayground(SampleDesign):
...     @inline
...     class circuit(Circuit):
...         silly_port = Port()
...         ...
"""

from jitx.board import Board
from jitx.container import Composite
from jitx.design import Design
from jitx.feature import Silkscreen
from jitx.layerindex import Side
from jitx.logo import LOGO
from jitx.shapes.composites import rectangle
from jitx.si import (
    DifferentialRoutingStructure,
    RoutingStructure,
    symmetric_routing_layers,
)
from jitx.stackup import Conductor, Dielectric, Material, Stackup
from jitx.substrate import FabricationConstraints, Substrate
from jitx.transform import Transform
from jitx.units import ohm
from jitx.via import Via, ViaType


class SoldermaskLayer(Dielectric):
    pass


class Core(Dielectric):
    pass


class Prepreg(Dielectric):
    pass


class Copper(Conductor):
    pass


class SampleStackup(Stackup):
    top_surface = SoldermaskLayer(thickness=0.1)
    layers: list[Material]
    bottom_surface = SoldermaskLayer(thickness=0.1)

    def __init__(self, layer_count: int):
        self.layers = []
        for i in range(layer_count):
            if i:
                if i % 2:
                    self.layers.append(Core(thickness=0.55))
                else:
                    self.layers.append(Prepreg(thickness=0.1))
            if i == 0:
                name = "Top"
            elif i == layer_count - 1:
                name = "Bottom"
            elif i < layer_count // 2:
                name = f"Top + {i}"
            else:
                name = f"Bottom - {layer_count - i - 1}"
            self.layers.append(Copper(thickness=0.1, name=name))


class SampleTwoLayerStackup(SampleStackup):
    def __init__(self):
        super().__init__(2)


class SampleFabConstraints(FabricationConstraints):
    min_copper_width = 0.127
    min_copper_copper_space = 0.127
    min_copper_hole_space = 0.2032
    min_copper_edge_space = 0.5

    min_annular_ring = 0.1524
    min_drill_diameter = 0.254
    min_silkscreen_width = 0.127
    min_pitch_leaded = 0.35
    min_pitch_bga = 0.35

    max_board_width = 456.2
    max_board_height = 609.6

    min_silk_solder_mask_space = 0.15
    min_silkscreen_text_height = 1.0
    solder_mask_registration = 0.15
    min_soldermask_opening = 0.152
    min_soldermask_bridge = 0.102

    min_th_pad_expand_outer = 0.1
    min_hole_to_hole = 0.254
    min_pth_pin_solder_clearance = 3.0


class SampleSubstrate(Substrate):
    """Sample substrate using a two layer stackup and the sample fabrication
    constraints."""

    stackup = SampleTwoLayerStackup()
    constraints = SampleFabConstraints()

    class MicroVia(Via):
        start_layer = 0
        stop_layer = 1
        diameter = 0.3
        hole_diameter = 0.1
        filled = True
        tented = Side.Top
        type = ViaType.LaserDrill

    class THVia(Via):
        start_layer = 0
        stop_layer = -1
        diameter = 0.45
        hole_diameter = 0.3
        type = ViaType.MechanicalDrill

    RS_50 = RoutingStructure(
        impedance=50 * ohm,
        layers=symmetric_routing_layers(
            {
                0: RoutingStructure.Layer(
                    trace_width=0.1176,
                    clearance=0.2,
                    velocity=191335235228,
                    insertion_loss=0.0178,
                )
            }
        ),
    )

    DRS_100 = DifferentialRoutingStructure(
        name="100 Ohm Differential Routing Structure",
        impedance=100 * ohm,
        layers=symmetric_routing_layers(
            {
                0: DifferentialRoutingStructure.Layer(
                    trace_width=0.09,
                    pair_spacing=0.137,
                    clearance=0.2,
                    velocity=191335235228,
                    insertion_loss=0.0178,
                )
            }
        ),
        uncoupled_region=RoutingStructure(
            name="100 Ohm Differential Routing Structure, Uncoupled",
            impedance=100 * ohm,
            layers=symmetric_routing_layers(
                {
                    0: RoutingStructure.Layer(
                        trace_width=0.09,
                        clearance=0.2,
                        velocity=191335235228,
                        insertion_loss=0.0178,
                    )
                }
            ),
        ),
    )


class SampleLogo(Composite):
    logo = [Silkscreen(x) for x in LOGO]


class SampleBoard(Board):
    """50 x 50mm rectangle board with rounded corners."""

    shape = rectangle(50, 50, radius=5)

    logo = SampleLogo(Transform((14, -24), 0, 0.02))


class SampleDesign(Design):
    """This is a base class for making sample designs, it has the sample board
    shape and substrate defined, but no main circuit."""

    substrate = SampleSubstrate()
    board = SampleBoard()

    # no main circuit here, add your own.
