import math

import jitx.test
from jitx.board import Board
from jitx.circuit import Circuit
from jitx.component import Component
from jitx.copper import Copper, Pour
from jitx.design import Design
from jitx.feature import Courtyard, Cutout, Silkscreen
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.layerindex import Side
from jitx.net import Net, Port
from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline, Polygon
from jitx.stackup import Conductor, Dielectric, Stackup
from jitx.substrate import FabricationConstraints, Substrate
from jitx.symbol import Symbol, Pin, Direction, SymbolMapping
from jitx.transform import Transform
from jitx.via import Via, ViaType


class TicTacToeBoard(Board):
    dim = 25.0
    shape = Polygon([(dim, dim), (dim, -dim), (-dim, -dim), (-dim, dim)])


class DefaultVia(Via):
    start_layer = 0
    stop_layer = 1
    diameter = 0.3
    hole_diameter = 0.1
    # filled = True
    # tented = Side.Top
    type = ViaType.LaserDrill


class TicTacToeConductor(Conductor):
    pass


class TicTacToeStackup(Stackup):
    layers = [
        Dielectric(thickness=0.1),
        TicTacToeConductor(thickness=0.1),
        Dielectric(thickness=0.1),
        TicTacToeConductor(thickness=0.1),
        Dielectric(thickness=0.1),
    ]


class TicTacToeFabConstraints(FabricationConstraints):
    min_copper_width = 0.127
    min_copper_copper_space = 0.127
    min_copper_hole_space = 0.127
    min_copper_edge_space = 0.127

    min_annular_ring = 0.127
    min_drill_diameter = 0.127
    min_silkscreen_width = 0.127
    min_pitch_leaded = 0.127
    min_pitch_bga = 0.127

    max_board_width = 50.0
    max_board_height = 50.0

    min_silk_solder_mask_space = 0.127
    min_silkscreen_text_height = 0.127
    solder_mask_registration = 0.127
    min_soldermask_opening = 0.127
    min_soldermask_bridge = 0.127

    min_th_pad_expand_outer = 0.127
    min_hole_to_hole = 0.127
    min_pth_pin_solder_clearance = 0.127


class TicTacToeSubstrate(Substrate):
    stackup = TicTacToeStackup()
    constraints = TicTacToeFabConstraints()
    vias = [DefaultVia]


def n_gon_points(sides, radius, reverse=False, trim=False):
    """Generate points for an n-sided polygon."""
    min_idx = 4 if trim else 0
    max_idx = sides - min_idx

    points = []
    if reverse:
        idx_range = range(max_idx, min_idx - 1, -1)
    else:
        idx_range = range(min_idx, max_idx + 1)

    for i in idx_range:
        angle = 2.0 * math.pi * float(i) / float(sides)
        points.append((radius * math.cos(angle), radius * math.sin(angle)))

    return points


def n_gon(sides, radius, width):
    """Create an n-sided polygon with specified width."""
    points = []
    r_outer = radius + width
    r_inner = radius - width

    points.extend(n_gon_points(sides, r_outer, False))
    points.extend(n_gon_points(sides, r_inner, True))

    return Polygon(points)


def n_star(spokes, radius, coeff, circle):
    """Create a star shape with specified parameters."""
    sides = 2 * spokes
    points = []
    r_outer = radius
    r_inner = radius * coeff
    cr = radius * circle

    min_idx = 2
    max_idx = sides - min_idx

    for i in range(min_idx, max_idx):
        angle = 2.0 * math.pi * float(i) / float(sides)
        points.append((r_outer * math.cos(angle), r_outer * math.sin(angle)))

        if i % 2 == 1:
            if i == max_idx - 1:
                angle1 = 2.0 * math.pi * (0.5 + float(i)) / float(sides)
                points.append((r_inner * math.cos(angle1), r_inner * math.sin(angle1)))

                points.extend(n_gon_points(sides, cr, True, trim=True))

                angle2 = (
                    2.0 * math.pi * (0.5 + float(sides + min_idx - 1)) / float(sides)
                )
                points.append((r_inner * math.cos(angle2), r_inner * math.sin(angle2)))
            else:
                angle = 2.0 * math.pi * (0.5 + float(i)) / float(sides)
                points.append((r_inner * math.cos(angle), r_inner * math.sin(angle)))

    return Polygon(points)


def plus_polygon(dim, width):
    """Create a plus-shaped polygon."""
    d = float(dim)
    nd = -d
    w = float(width)
    nw = -w

    points = [
        (nw, d),
        (w, d),
        (w, w),
        (d, w),
        (d, nw),
        (w, nw),
        (w, nd),
        (nw, nd),
        (nw, nw),
        (nd, nw),
        (nd, w),
        (nw, w),
    ]

    return Polygon(points)


class CircleModule(Circuit):
    """Circle module for the tic-tac-toe board."""

    def __init__(self):
        self.width = 4.0
        self.poly = n_gon(50, self.width, 1.0)
        self.gnd = Net(name="GND")
        self.features = []

        # Setup geometry
        self.via_positions = [
            (0.0, 0.0),
            (0.0, self.width),
            (self.width, 0.0),
            (0.0, -self.width),
            (-self.width, 0.0),
        ]

        # Create vias
        for pos in self.via_positions:
            self.gnd += DefaultVia().at(pos)

        # Add copper pour
        copper_pour = Pour(self.poly, 0, isolate=0.508, orphans=True)
        self.gnd += copper_pour

        # Add courtyard
        courtyard = Courtyard(self.poly)
        courtyard.side = Side.Top
        self.features.append(courtyard)


class XModule(Circuit):
    """X module for the tic-tac-toe board."""

    def __init__(self):
        poly_shape = plus_polygon(5, 1)
        self.poly = Shape(poly_shape, Transform.rotate(45))
        self.gnd = Net(name="GND")
        self.features = []

        # Setup vias at key positions
        self.via_positions = [
            (2.5, 2.5),
            (-2.5, 2.5),
            (2.5, -2.5),
            (-2.5, -2.5),
            (0.0, 0.0),
        ]

        # Create vias
        for pos in self.via_positions:
            self.gnd += DefaultVia().at(pos[0], pos[1])

        # Add copper pour
        copper_pour = Pour(self.poly, layer=0, isolate=0.508, orphans=True)
        self.gnd += copper_pour

        # Add courtyard
        courtyard = Courtyard(self.poly)
        courtyard.side = Side.Top
        self.features.append(courtyard)


class StarModule(Circuit):
    """Star module for the tic-tac-toe board."""

    def __init__(self):
        self.star = n_star(16, 5.0, 0.6, 0.1)
        self.gnd = Net(name="GND")
        self.features = []

        # Add via at center
        self.gnd += DefaultVia()

        # Add features
        cutout = Cutout(self.star)
        courtyard = Courtyard(self.star)

        self.features.append(cutout)
        self.features.append(courtyard)


class SquarePad(Pad):
    """A square SMD pad."""

    def __init__(self):
        self.shape = Polygon([(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)])
        self.type = "SMD"


class PassiveLandpattern(Landpattern):
    """Landpattern for passive components."""

    def __init__(self, with_via=False):
        # Create square pads
        self.pad1 = SquarePad().at(Transform.translate(-0.75, 0.0))
        self.pad2 = SquarePad().at(Transform.translate(0.75, 0.0))

        # Add via if requested
        if with_via:
            self.via = DefaultVia().at(0.0, 0.5)

        # Add courtyard
        courtyard = Courtyard(
            Polygon([(2.0, 1.0), (2.0, -1.0), (-2.0, -1.0), (-2.0, 1.0)])
        )
        courtyard.side = Side.Top
        self.courtyard = courtyard


class PassiveSymbol(Symbol):
    """Symbol for passive components."""

    def __init__(self):
        # Create pins
        self.p1 = Pin(at=(-2, 0), direction=Direction.Left, length=2)
        self.p2 = Pin(at=(2, 0), direction=Direction.Right, length=2)

        # Add symbol graphics
        self.draw = Polyline(0.2, [(-1.0, 0.0), (1.0, 0.0)])


class PassiveComponent(Component):
    """Passive component for the design."""

    def __init__(self, with_via=False):
        self.landpattern = PassiveLandpattern(with_via)
        self.symbol = PassiveSymbol()
        self.p1 = Port()
        self.p2 = Port()

        # Create mappings between ports, pins and pads
        self.mappings = [
            PadMapping(
                {self.p1: self.landpattern.pad1, self.p2: self.landpattern.pad2}
            ),
            SymbolMapping({self.p1: self.symbol.p1, self.p2: self.symbol.p2}),
        ]


class CoppersModule(Circuit):
    """Module for copper traces."""

    def __init__(self):
        self.gnd = Net(name="GND")

        # Add via
        self.gnd += DefaultVia().at(0.0, -16.5)

        # Add copper traces
        line1 = Polyline(0.2, [(-16.5, 0.0), (0.0, -16.5)])
        line2 = Polyline(0.2, [(16.5, 0.0), (0.0, -16.5)])

        self.gnd += Copper(line1, 0)
        self.gnd += Copper(line2, 0)


class TicTacToeDesignCircuit(Circuit):
    """Main circuit for the tic-tac-toe design."""

    def __init__(self):
        self.features = []

        # Feature toggles
        self.use_circles = False
        self.use_stars = False
        self.use_x = False

        # Create instances
        self.circles = [CircleModule() for _ in range(3)]
        self.stars = [StarModule() for _ in range(2)]
        self.xs = [XModule() for _ in range(3)]
        self.passive = PassiveComponent(False)
        self.coppers = CoppersModule()

        # Place components if enabled
        if self.use_circles:
            self.place(self.circles[0], Transform.translate(-16.5, -16.5))
            self.place(self.circles[1], Transform.translate(0.0, -16.5))
            self.place(self.circles[2], Transform.translate(16.5, -16.5))

        if self.use_stars:
            transform = Transform.translate(-16.5, 0.0) * Transform.rotate(180)
            self.place(self.stars[0], transform)
            self.place(self.stars[1], Transform.translate(16.5, 0.0))

        if self.use_x:
            self.place(self.xs[0], Transform.translate(-16.5, 16.5))
            self.place(self.xs[1], Transform.translate(0.0, 16.5))
            self.place(self.xs[2], Transform.translate(16.5, 16.5))

        # Create nets
        self.c_net = Net(name="C")
        for circle in self.circles:
            self.c_net += circle.gnd

        self.x_net = Net(name="X")
        for x in self.xs:
            self.x_net += x.gnd

        self.s_net = Net(name="S")
        for star in self.stars:
            self.s_net += star.gnd

        # Connect everything to GND
        self.gnd = Net(name="GND")
        self.gnd += self.c_net
        self.gnd += self.x_net
        self.gnd += self.s_net
        self.gnd += self.passive.p1
        self.gnd += self.passive.p2
        self.gnd += self.coppers.gnd

        # Create grid lines
        self.create_grid_lines()

    def create_grid_lines(self):
        """Create the grid lines for the tic-tac-toe board."""
        num_sections = 3
        width = 50.0  # board_shape width
        height = 50.0  # board_shape height
        section_width = width / float(num_sections)
        section_height = height / float(num_sections)

        # Create vertical lines
        for i in range(1, num_sections):
            line_x = section_width * i
            points = [
                (line_x - width / 2, 1.0 - height / 2),
                (line_x - width / 2, height - 1.0 - height / 2),
            ]
            line = Polyline(0.25, points)

            silkscreen = Silkscreen(line)
            silkscreen.side = Side.Top
            self.features.append(silkscreen)

        # Create horizontal lines
        for i in range(1, num_sections):
            line_y = section_height * i
            points = [
                (1.0 - width / 2, line_y - height / 2),
                (width - 1.0 - width / 2, line_y - height / 2),
            ]
            line = Polyline(0.25, points)

            silkscreen = Silkscreen(line)
            silkscreen.side = Side.Top
            self.features.append(silkscreen)


class TicTacToeDesign(Design):
    """Complete tic-tac-toe design."""

    board = TicTacToeBoard()
    substrate = TicTacToeSubstrate()
    circuit = TicTacToeDesignCircuit()


class TicTacToeTest(jitx.test.TestCase):
    """Test case for the tic-tac-toe design."""

    def test_instantiate_and_translate_design(self):
        """Test instantiating and translating the design."""
        design = TicTacToeDesign()

        # Translate the design
        import jitx._translate.design

        jitx._translate.design.package_design(design)
