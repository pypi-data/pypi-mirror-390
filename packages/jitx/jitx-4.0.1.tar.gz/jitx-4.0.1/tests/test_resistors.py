from jitx.board import Board
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.constraints import UnaryDesignConstraint as UnaryDesignRule, TrueExpr
from jitx.container import Composite
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.net import Net, Port, PortAttachment
from jitx.schematic import (
    AuthorRow,
    AuthorTable,
    DataCell,
    SchematicTemplate,
    SchematicMarking,
    SchematicTitlePage,
    TableCell,
)
from jitx.shapes.composites import rectangle
from jitx.symbol import Symbol, SymbolMapping, Pin, Direction, SymbolOrientation
from jitx.shapes.primitive import Polygon, Polyline
from jitx.anchor import Anchor
from jitx.sample import SampleDesign, SampleSubstrate
from jitx.feature import (
    Silkscreen,
    Soldermask,
    Courtyard,
)

import unittest
import jitx.test
from jitx.transform import Transform
from jitx.shapes import Shape
from jitx.landpattern import PadShape


# TODO: Make this a Pad method?
def pad_shape(p: Pad) -> Shape:
    if isinstance(p.shape, PadShape):
        return p.shape.shape
    else:
        return p.shape


class ResistorBoard(Board):
    # Create a rectangular board that's large enough for our resistor circuit
    shape = Polygon(
        [
            (-10, -5),  # bottom left
            (10, -5),  # bottom right
            (10, 5),  # top right
            (-10, 5),  # top left
        ]
    )


class ResistorPad(Pad):
    shape = Polygon([(-0.4, 0.4), (0.4, 0.4), (0.4, -0.4), (-0.4, -0.4)])

    def __init__(self):
        self.soldermask = Soldermask(pad_shape(self))


class ResistorLandpattern(Landpattern):
    # Two pads for a resistor, one at each end
    pad1 = ResistorPad().at(-0.5, 0)
    pad2 = ResistorPad().at(0.5, 0)

    # Add silkscreen to show resistor body with zigzag pattern
    silkscreen = Silkscreen(
        Polyline(
            0.1,
            [
                (-0.4, 1),  # Start at left pad
                (-0.3, 1.2),  # First zig
                (-0.2, 0.8),  # First zag
                (-0.1, 1.2),  # Second zig
                (0, 0.8),  # Second zag
                (0.1, 1.2),  # Third zig
                (0.2, 0.8),  # Third zag
                (0.3, 1.2),  # Fourth zig
                (0.4, 1),  # End at right pad
            ],
        )
    )

    # Add courtyard
    courtyard = Courtyard(rectangle(2, 1))

    def __init__(self):
        self.sub = Composite(Transform.rotate(45))


class ResistorSymbol(Symbol):
    # Two pins for a resistor
    pin1 = Pin(at=(-2, 0), length=1, direction=Direction.Left)
    pin2 = Pin(at=(2, 0), length=1, direction=Direction.Right)

    # Draw resistor body with zigzag pattern
    draw = [
        # Main zigzag pattern
        Polyline(
            0.15,
            [
                (-2.0, 0),
                (-1.05, 0),  # First zig
            ],
        ),
        Polyline(
            0.25,
            [
                (-1.05, -0.04),  # First zig
                (-0.9, -0.3),  # First zag
                (-0.6, 0.3),  # Second zig
                (-0.3, -0.3),  # Second zag
                (0, 0.3),  # Third zig
                (0.3, -0.3),  # Third zag
                (0.6, 0.3),  # Fourth zig
                (0.9, -0.3),  # Fourth zag
                (1.05, -0.04),  # Fifth zig
            ],
        ),
        Polyline(
            0.15,
            [
                (1.05, 0),  # Fifth zig
                (2.0, 0),
            ],
        ),
    ]

    orientation = SymbolOrientation(0)


class ResistorComponent(Component):
    landpattern = ResistorLandpattern()
    symbol = ResistorSymbol()

    # Two ports for the resistor
    p1 = Port()
    p2 = Port()

    mpn = "RES-0805"
    manufacturer = "Generic"
    datasheet = "https://www.example.org/resistor-datasheet"
    reference_designator_prefix = "R"

    def __init__(self, no_connect: int | None = None):
        self.mappings = [
            SymbolMapping({self.p1: self.symbol.pin1, self.p2: self.symbol.pin2}),
            PadMapping(
                {self.p1: self.landpattern.pad1, self.p2: self.landpattern.pad2}
            ),
        ]

        if no_connect:
            if no_connect == 1:
                self.p1.no_connect()
            elif no_connect == 2:
                self.p2.no_connect()
            else:
                print("no_connect is not 1 or 2")


class ResistorCircuit(Circuit):
    # Create a few resistors
    r1 = ResistorComponent(1)
    r2 = ResistorComponent()
    r3 = ResistorComponent(2)

    def __init__(self):
        # Place resistors in a series configuration
        self.place(self.r1, Transform.translate(-3, 0))
        self.place(self.r2, Transform.translate(0, 0))
        self.place(self.r3, Transform.translate(3, 0))

        # Connect resistors in series
        self.nets = [
            Net([self.r1.p2, self.r2.p1]),
            Net([self.r2.p2, self.r3.p1]),
        ]

        self.r1.p1.no_connect()
        self.r3.p2.no_connect()

        rect = rectangle(3, 3).to_shapely()
        rect = rect.difference(rect.buffer(-0.1))
        self.r1.landpattern.boxed = Silkscreen(rect)
        # Set component status
        for comp in [self.r1, self.r2, self.r3]:
            comp.in_bom = True
            comp.soldered = True
            comp.schematic_x_out = False

        self.attachments = [
            PortAttachment(self.r1.p1, SampleSubstrate.MicroVia().at(-5, 0)),
            PortAttachment(self.r3.p2, SampleSubstrate.MicroVia().at(5, 0)),
        ]


class ResistorSchematicTemplate(SchematicTemplate):
    width = 108
    height = 32
    table = AuthorTable(
        rows=[
            AuthorRow(
                cells=[
                    DataCell(value=">TITLE", width=0.7),
                    TableCell(
                        table=AuthorTable(
                            rows=[
                                AuthorRow(cells=[DataCell(value="JITX Inc.")]),
                                AuthorRow(
                                    cells=[DataCell(value="sheet >SHEET/>NUMSHEETS")],
                                    height=0.3,
                                ),
                            ]
                        ),
                    ),
                ],
            ),
            AuthorRow(
                cells=[DataCell(value="May 13, 2025")],
                height=0.2,
            ),
        ]
    )


class ResistorDesign(SampleDesign):
    circuit = ResistorCircuit()
    schematic_template = ResistorSchematicTemplate()

    def __init__(self):
        self.rules = []
        self.rules.append(UnaryDesignRule(TrueExpr()).trace_width(0.2))

        self.schematic_markings = []
        self.schematic_markings.append(
            SchematicMarking(
                '<g><text x="-55" y="0" font-family="Arial" font-size="20" fill="black">Resistor Test</text></g>',
                Anchor.S,
            )
        )

        self.schematic_title_page = SchematicTitlePage(
            """<svg width="279" height="216" viewBox="0 0 279 216" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#2C3E50" />
                        <stop offset="100%" stop-color="#3498DB" />
                    </linearGradient>
                </defs>
                <rect x="0" y="0" width="279" height="216" rx="10" fill="url(#bgGradient)" />
                <text x="50" y="110" font-family="Arial, Helvetica, sans-serif" font-size="50" fill="white" font-weight="bold">Resistor Test</text>
            </svg>""",
        )


class RawInstantiableTest(unittest.TestCase):
    def test_raw_design_is_instantiable(self):
        import jitx._structural

        design = ResistorDesign()
        self.assertIsInstance(design, jitx._structural.Instantiable)


class ResistorTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = ResistorDesign()
        self.assertIsInstance(design.circuit, ResistorCircuit)

        import jitx._translate.design

        jitx._translate.design.package_design(design)
