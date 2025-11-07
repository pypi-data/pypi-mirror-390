# ruff: noqa: B905
# we do a lot of zip shenaningans in this file.
from dataclasses import dataclass
from itertools import chain, count

from jitx.board import Board
from jitx.component import Component
from jitx.circuit import Circuit, SchematicGroup

# from jitx.model3d import Model3D
from jitx.paper import Paper
from jitx.placement import Placement
from jitx.property import Property
from jitx.constraints import (
    IsTrace,
    IsPad,
    OnLayer,
    TrueExpr,
    ViaFencePattern,
    UnaryDesignConstraint as UnaryDesignRule,
    BinaryDesignConstraint as BinaryDesignRule,
    design_constraint as rule,
    SquareViaStitchGrid,
    TriangularViaStitchGrid,
    Tag,
)
from jitx.container import Composite, inline
from jitx.context import Context
from jitx.events import Event
from jitx.inspect import extract, visit
from jitx.landpattern import Landpattern, Pad, PadMapping, PadShape
from jitx.layerindex import Side
from jitx.net import DiffPair, Net, Port, Provide, ShortTrace, provide
from jitx.copper import Copper, Pour
from jitx.shapes import Shape
from jitx.si import (
    BridgingPinModel,
    DifferentialRoutingStructure,
    RoutingStructure,
)
from jitx.schematic import (
    AuthorRow,
    AuthorTable,
    DataCell,
    SchematicTemplate,
    SchematicMarking,
    SchematicTitlePage,
    TableCell,
)
from jitx.shapes.composites import rectangle, capsule
from jitx.shapes.shapely import ShapelyGeometry
from jitx.si import Constrain, ConstrainDiffPair, Topology
from jitx.symbol import Symbol, SymbolMapping, Pin, Direction, SymbolOrientation
from jitx.design import Design, DesignContext
from jitx.shapes.primitive import Circle, Polygon, Polyline, Text
from jitx.anchor import Anchor
from jitx.si import PinModel
from jitx.substrate import FabricationConstraints, Substrate
from jitx.stackup import Conductor, Dielectric, Material, Stackup
from jitx.feature import (
    Silkscreen,
    Soldermask,
    Paste,
    Glue,
    Finish,
    Courtyard,
    Cutout,
    KeepOut,
    Custom,
)

from jitx.units import kohm, ohm

import unittest
import jitx.test
from jitx.toleranced import Toleranced
from jitx.via import Backdrill, BackdrillSet, Via, ViaType, ViaDiameter
from jitx.transform import Transform


# TODO: Make this a Pad method?
def pad_shape(p: Pad) -> Shape:
    if isinstance(p.shape, PadShape):
        return p.shape.shape
    else:
        return p.shape


@dataclass
class VerifyEvent(Event):
    case: jitx.test.TestCase


class CopperConductor(Conductor):
    pass


class SmokeStackup(Stackup):
    layers: list[Material] = [
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1, name="Front Bun"),
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1, name="Lettuce"),
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1, name="Tomato"),
        Dielectric(thickness=0.1),
        CopperConductor(thickness=0.1, name="Back Bun"),
        Dielectric(thickness=0.1),
    ]


class SmokeFabConstraints(FabricationConstraints):
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


class SmokeVia(Via):
    start_layer = 0
    stop_layer = 1
    diameter = 0.3  # ViaDiameter(0.3, nfp=0.2)
    hole_diameter = 0.1
    filled = True
    tented = Side.Top
    type = ViaType.LaserDrill
    models = {(0, 1): PinModel(0.01, 0.02)}


class SmokeBackdrillVia(SmokeVia):
    diameter = ViaDiameter(pad=0.5, nfp=0.35)
    backdrill = BackdrillSet(
        top=Backdrill(
            diameter=0.1,
            startpad_diameter=0.2,
            solder_mask_opening=0.3,
            copper_clearance=0.4,
        ),
        bottom=Backdrill(
            diameter=0.1,
            startpad_diameter=0.2,
            solder_mask_opening=0.3,
            copper_clearance=0.4,
        ),
    )
    diameters = {
        1: ViaDiameter(pad=0.2, nfp=0.7),
        0: ViaDiameter(pad=0.15),
    }


class SmokeSubstrate(Substrate):
    stackup = SmokeStackup()
    constraints = SmokeFabConstraints()
    vias = [SmokeVia, SmokeBackdrillVia]


class SmokeBoard(Board):
    shape = ShapelyGeometry.from_shape(
        rectangle(50, 50, chamfer=(0, 0, 3, 5), radius=(0, 3, 0, 2))
    ).difference(ShapelyGeometry.from_shape(Circle(radius=2).at(-22, 22)))


class SmokeRoutingStructure(RoutingStructure):
    def __init__(self):
        super().__init__(
            impedance=37 * ohm,
            layers={
                0: RoutingStructure.Layer(
                    trace_width=0.5, velocity=3.0, insertion_loss=0.05
                ),
                1: RoutingStructure.Layer(
                    trace_width=0.3, velocity=3.0, insertion_loss=0.05
                ),
            },
        )


class SmokeDifferentialRoutingStructure(DifferentialRoutingStructure):
    def __init__(self):
        super().__init__(impedance=50 * ohm)

    uncoupled_region = SmokeRoutingStructure()
    layers = {
        0: DifferentialRoutingStructure.Layer(
            trace_width=0.5, velocity=3.0, insertion_loss=0.05, pair_spacing=0.2
        ),
        1: DifferentialRoutingStructure.Layer(
            trace_width=0.3, velocity=3.0, insertion_loss=0.05, pair_spacing=0.2
        ),
    }


class SmokePad(Pad):
    shape = Circle(diameter=0.8)

    def __init__(self):
        self.soldermask = Soldermask(pad_shape(self))


class SmokePadTH(Pad):
    shape = Circle(diameter=1.4).at(2.0, 1.0)
    shapes = {
        0: PadShape(
            Circle(diameter=0.8).at(2.0, 1.0),
            nfp=Circle(diameter=0.6).at(2.0, 1.0),
        ),
        2: Circle(diameter=0.7).at(2.0, 1.0),
        -1: PadShape(
            rectangle(3.0, 1.5).at(2.0, 1.0),
            nfp=rectangle(2.5, 1.5).at(2.0, 1.0),
        ),
    }

    def __init__(self):
        self.cutout = Cutout(Circle(diameter=0.4).at(2, 1.0))
        self.soldermask = Soldermask(pad_shape(self))


class SmokePadTwo(Pad):
    shape = rectangle(1, 1, chamfer=(0.381, 0.2, 0.381, 0))


# test tweaking knobs...
BANKSZ = 6
COMPONENTS = 4
CIRCUITS = 4

# 1000/5/3 => 30 000 pins
# number of pins is BANKSZ * 2 * COMPONENTS * CIRCUITS
# print(BANKSZ * 2 * COMPONENTS * CIRCUITS, 'pins')


class SmokeNCPads(Landpattern):
    u = SmokePad().at(0, 1)
    v = SmokePad().at(0, -1)


class SmokeLandFirst(Landpattern):
    pads = [
        SmokePad().at(i, 0, on=Side.Top if i & 1 else Side.Bottom)
        for i in range(-BANKSZ, BANKSZ)
    ]
    nc = SmokeNCPads().at(0, 0)
    unmapped_pad = SmokePad().at(0, 2)


# Add one of each Feature type in a circular arrangement
circle_radius = 1.0
arrangement_radius = 6.0


class SmokeLandCustom(Landpattern):
    custom = Custom(
        Circle(radius=circle_radius).at(
            -arrangement_radius * 0.7071, -arrangement_radius * 0.7071
        ),
        name="MyCustomLayer",
    )


class SmokeLandSecond(Landpattern):
    c1 = SmokePadTH() @ (0, 1)
    c1_2 = SmokePadTwo() @ (1, 1)
    c2 = SmokePadTH() @ (0, -1)
    c34 = {
        "c.3": SmokePad().at(0, 2, on=Side.Bottom),
        4: SmokePad().at(0, -2, on=Side.Bottom),
    }

    valuetext = Silkscreen(Text(">VALUE", 1, Anchor.C))
    silkscreen = Silkscreen(Circle(radius=circle_radius).at(arrangement_radius, 0))
    soldermask = Soldermask(
        Circle(radius=circle_radius).at(
            arrangement_radius * 0.7071, arrangement_radius * 0.7071
        )
    )
    paste = Paste(Circle(radius=circle_radius).at(0, arrangement_radius))
    glue = Glue(
        Circle(radius=circle_radius).at(
            -arrangement_radius * 0.7071, arrangement_radius * 0.7071
        )
    )
    finish = Finish(
        Circle(radius=circle_radius).at(
            -arrangement_radius * 0.7071, arrangement_radius * 0.7071
        )
    )
    courtyard = Courtyard(Circle(radius=circle_radius).at(0, 0))
    cutout = Cutout(
        Transform.translate(0, -arrangement_radius)
        * capsule(circle_radius, 2 * circle_radius)
    )
    # board_edge = BoardEdge(<Line only, not yet supported>)
    keep_out = KeepOut(
        Circle(radius=circle_radius).at(
            arrangement_radius * 0.7071, -arrangement_radius * 0.7071
        ),
        layers=jitx.layerindex.LayerSet.range(0, through=1),
        pour=True,
        route=True,
    )

    customsub = SmokeLandCustom()
    customized = Custom(
        Text("2nd", size=1).at(
            -arrangement_radius * 0.7071, -arrangement_radius * 0.7071
        ),
        name="Second Custom",
    )

    # model = Model3D("APHB1608.step", rotation=(90, 0, 0))

    def __init__(self):
        self.sub = Composite(Transform.rotate(45))
        self.sub.silkscreen = Silkscreen(Polygon([(1, 1), (-1, 1), (-1, -1), (1, -1)]))

    @VerifyEvent.on
    def verify(self, event: VerifyEvent):
        for trace, elem in visit(self, Silkscreen):
            if elem is self.sub.silkscreen:
                assert trace.transform is not None
                event.case.assertEqual(trace.transform._rotate, 45)
                return
        event.case.assertTrue(False, "No silkscreen found")


class SmokeSymbol(Symbol):
    a = [
        Pin(
            at=(i, 1),
            length=3,
            direction=Direction.Up,
            pin_name_size=0.1,
            pad_name_size=0.1,
        )
        for i in range(BANKSZ // 2)
    ]
    b = [
        Pin(
            at=(i, -1),
            length=3,
            direction=Direction.Down,
            pin_name_size=0.1,
            pad_name_size=0.1,
        )
        for i in range(BANKSZ // 2)
    ]
    c1 = Pin(at=(-1, 0), length=3, direction=Direction.Left)
    c2 = Pin(at=(1, 0), length=3, direction=Direction.Right)
    pin_name_size = 0.15
    pad_name_size = 0.25

    def __init__(self):
        self.draw = (Circle(radius=3).at(0, 2), Circle(radius=2).at(0, -1))
        self.sub = Composite(Transform.rotate(-135))
        self.sub.other = [
            Circle(radius=1).at(1, 0),
            Text("Hello, world!", 1, Anchor.C).at(0, -5),
        ]


class SmokeGNDSymbol(Symbol):
    a = [Pin(at=(0, 1), length=0, direction=Direction.Up)]
    draw = [
        Polyline(0.1, [(0, 0), (0, 1)]),
        Polyline(0.1, [(-0.7, 0), (0.7, 0)]),
        Polyline(0.1, [(-0.5, -0.3), (0.5, -0.3)]),
        Polyline(0.1, [(-0.3, -0.6), (0.3, -0.6)]),
        Text(">REF", 0.1, Anchor.C).at(0, -0.6),
    ]
    orientation = SymbolOrientation(0)


class DoublePort(Port):
    u = Port()
    v = Port()


@dataclass
class ComponentData(Context):
    dummy: int


class SmokeComponent(Component):
    component_data = ComponentData(5)
    value = 100 * kohm

    landfirst = SmokeLandFirst()
    landsecond = SmokeLandSecond().at(0.75, 0)
    symbol = SmokeSymbol()
    second_symbol = SmokeSymbol()

    @inline
    class NCSymbol(Symbol):
        u = Pin(at=(0, 1), length=1, direction=Direction.Up)
        v = Pin(at=(0, -1), length=1, direction=Direction.Down)
        box = rectangle(2, 2)

    a = [Port() for _ in range(BANKSZ)]
    b = [DoublePort() for _ in range(BANKSZ // 2)]

    p1 = DoublePort()
    p2 = {"p.2": DoublePort()}

    ncPort = DoublePort()

    mpn = "MPN"
    manufacturer = "MFG"
    datasheet = "https://www.example.org/datasheet"
    reference_designator_prefix = "Q"

    @provide(DoublePort)
    def doubleport(self, p: DoublePort):
        return [
            {p: self.p1},
            {p.u: self.p2["p.2"].u, p.v: self.p2["p.2"].v},
        ]

    cmappings = [
        SymbolMapping(
            {
                p1.u: symbol.c1,
                p1.v: symbol.c2,
                p2["p.2"].u: second_symbol.c1,
                p2["p.2"].v: second_symbol.c2,
                ncPort.u: NCSymbol.u,
                ncPort.v: NCSymbol.v,
            }
        ),
        PadMapping(
            {
                p1.u: [landsecond.c1, landsecond.c1_2],
                p1.v: landsecond.c2,
                p2["p.2"].u: landsecond.c34["c.3"],
                p2["p.2"].v: landsecond.c34[4],
                ncPort.u: landfirst.nc.u,
                ncPort.v: landfirst.nc.v,
            }
        ),
        BridgingPinModel(
            p1.u,
            p1.v,
            delay=Toleranced.exact(1.0),
            loss=Toleranced.exact(1.0),
        ),
    ]

    def __init__(self):
        self.ncPort.u.no_connect()
        self.mappings = [
            SymbolMapping(
                (port_a, pin_a)
                for port_a, pin_a in zip(self.a, chain(self.symbol.a, self.symbol.b))
            ),
            SymbolMapping(
                chain.from_iterable(
                    ((port_b.u, pin_ba), (port_b.v, pin_bb))
                    for port_b, (pin_ba, pin_bb) in zip(
                        self.b, zip(self.second_symbol.a, self.second_symbol.b)
                    )
                )
            ),
            PadMapping(
                (port, pad) for port, pad in zip(self.a, self.landfirst.pads[:BANKSZ])
            ),
            PadMapping(
                chain.from_iterable(
                    ((port.u, pad_u), (port.v, pad_v))
                    for port, (pad_u, pad_v) in zip(
                        self.b,
                        zip(
                            self.landfirst.pads[BANKSZ::2],
                            self.landfirst.pads[BANKSZ + 1 :: 2],
                        ),
                    )
                )
            ),
        ]

    @VerifyEvent.on
    def _on_verify(self, verify: VerifyEvent):
        verify.case.assertEqual(ComponentData.require().dummy, 5)


@dataclass
class SmokeContext(Context):
    count: int = 0


class DoublePorts(Port):
    def __init__(self, count: int):
        self.ports = [DoublePort() for _ in range(count)]


class HighVoltage(Property):
    pass


class SmokeSubCircuit(Circuit):
    lots_of_components = [SmokeComponent() for _ in range(COMPONENTS)]
    SCH_GROUP = SchematicGroup(lots_of_components[0].symbol)
    UNIT_GROUP = SchematicGroup(lots_of_components[1].second_symbol)

    aports = [Port() for _ in range(BANKSZ)]
    bports = [DoublePort() for _ in range(BANKSZ // 2)]
    cports = [
        DoublePort(),
        DoublePort(),
    ]
    dports = [DiffPair() for _ in range(BANKSZ // 2)]

    coppers = [Copper(Circle(diameter=2.0).at(-6, 0), layer=0)]
    pours = [Pour(Circle(diameter=30.0), layer=0, isolate=1.0, rank=1)]

    dport = DoublePort()

    @provide(DoublePort)
    def self_provide(self, p: DoublePort):
        def mapping(comp: SmokeComponent):
            # cp = comp.require(DoublePort)
            cp = Provide.require(DoublePort, comp)
            return {
                p.u: cp.u,
                p.v: cp.v,
            }

        return [mapping(comp) for comp in self.lots_of_components]

    @provide.subset_of(DoublePorts(2), 1)
    def self_provide_2(self, p: DoublePorts):
        return [
            ((p.ports[0], self.cports[0]), (p.ports[1], self.cports[1])),
        ]

    def __init__(self, index: int):
        def remove_chunk(shape: Shape) -> Shape:
            shape = ShapelyGeometry.from_shape(shape)
            return shape.difference(shape.buffer(-0.2))

        self.index = index
        for comp in self.lots_of_components:
            comp.ncPort.v.no_connect()

        for i, comp in enumerate(self.lots_of_components):
            if i < len(comp.landfirst.pads):
                pad = comp.landfirst.pads[i]
                if isinstance(pad.shape, PadShape):
                    pad.shape = PadShape(
                        remove_chunk(pad.shape.shape),
                        nfp=pad.shape.nfp and remove_chunk(pad.shape.nfp),
                    )
                else:
                    pad.shape = remove_chunk(pad.shape)
                pad.marker = Silkscreen(Circle(diameter=1) @ (1, 1))
        for i in range(0, COMPONENTS, 2):
            self.place(
                self.lots_of_components[i],
                Transform.rotate(i * 360 / COMPONENTS) * Transform.translate(1, 3),
                on=Side.Bottom if i & 3 else Side.Top,
            )
            self.lots_of_components[i].in_bom = True
            self.lots_of_components[i].soldered = True
            self.lots_of_components[i].schematic_x_out = True
        self.nets = []
        self.short_traces = []
        self.topologies = []
        self.constraints = []
        self.nets.append(Net([self.aports[0]], name="GND", symbol=SmokeGNDSymbol()))
        GNDTag().assign(self.nets[-1])
        for i, comp in enumerate(self.lots_of_components):
            # Net single circuits ports to components ports.
            # Apply a net symbol.
            for our, their in zip(self.aports, comp.a):
                # net = our + their
                self.topologies.append(our >> their)
            # Net a single port within bundle ports to components ports.
            for our, their, num in zip(self.bports, comp.b, count()):
                self.nets.append(Net(name=f"NAMED_NET!🔥{num}-{i}") + our.u + their.u)
                self.nets.append(our.v + their.v)
            # Net bundle ports to components ports.
            for our, their in zip(self.bports, comp.b):
                self.nets.append(our + their)
            for our, their in zip(self.dports, comp.b):
                self.nets.append(our.p + their.u)
                self.nets.append(our.n + their.v)
                self.topologies += (our.p >> their.u, our.n >> their.v)
            # Request a bundle port from the component.
            require_comp = Provide.require(DoublePort, comp)
            require_self = self.require(DoublePort)
            self.nets += (
                require_self.u + require_comp.u,
                require_self.v + require_comp.v,
            )

            # Net all single component ports together.
            for prev, curr in zip(
                self.lots_of_components[0].a,
                self.lots_of_components[0].a[1:],
                strict=False,
            ):
                net = prev + curr
                self.nets.append(net)
                self.topologies.append(prev >> curr)

            self.topologies.append(self.bports[0].u >> comp.b[0].u)
            self.topologies.append(self.bports[1].v >> comp.b[1].v)

        # Net all single circuit ports together.
        for prev, curr in zip(self.aports, self.aports[1:]):
            self.nets.append(prev + curr)

        # Assign a routing structure to the topology.
        self.constraints.append(
            Constrain(
                Topology(
                    self.lots_of_components[0].a[0], self.lots_of_components[0].a[-1]
                )
            )
            .structure(SmokeRoutingStructure())
            .timing(1.0, 3.0)
            .insertion_loss(0.2, 0.5)
        )

        # Assign a differential routing structure to the diff pair ports.
        self.constraints.append(
            ConstrainDiffPair(Topology(self.dports[0], self.dports[1]))
            .structure(
                SmokeDifferentialRoutingStructure()
                # Assign a timing constraint to the ports.
            )
            .timing_difference(0, 1)
        )

        for port, copper, pour in zip(self.aports, self.coppers, self.pours):
            self.nets.append(port + copper + pour)

        self.place(
            self.lots_of_components[0],
            Transform.rotate(0) * Transform.translate(1, 0),
        )

        dportnet = self.dports[0] + self.dports[1]
        dportnet.name = "DPortNet"
        SpecialTag().assign(dportnet.port.p)
        self.nets.append(dportnet)

        pour_net = self.dports[0].n + Pour(
            Circle(diameter=10.0).at(0, 0), layer=0, isolate=1.0
        )
        pour_net.name = "custom"
        CustomTag().assign(pour_net)

        self += pour_net

        # self.topologies.append(Topology([self.dports[0], self.dports[1]]))
        # self.topologies.append(Topology([self.bports[0], self.bports[1]]))

        self.annotate(f"Hello, world {self.index}!")
        # self.reference(self.lots_of_components[0], "REF1")
        self.short_traces.append(
            ShortTrace(
                self.lots_of_components[0].a[0], self.lots_of_components[0].a[-1]
            )
        )

    @Design.Initialized.on
    def on_initialized(self):
        tc = ContextTest.get()
        if self.index < 2:
            if tc:
                tc.test.assertEqual(SmokeContext.require().count, 0)
            SmokeContext.require().count += 1
        else:
            if tc:
                tc.test.assertIsNone(SmokeContext.get())

    @VerifyEvent.on
    def _on_verify(self, verify: VerifyEvent):
        verify.case.assertIsNone(ComponentData.get())


class SmokeMainCircuit(Circuit):
    sub_circuits = [SmokeSubCircuit(i) for i in range(2, CIRCUITS)]
    sub_circuits[0].in_bom = False
    sub_circuits[0].soldered = False
    sub_circuits[0].schematic_x_out = True

    def __init__(self):
        tc = ContextTest.get()
        self.sub_circuits[0].lots_of_components[0].reference_designator = "o7"
        if tc:
            tc.test.assertIsInstance(jitx.current.substrate, SmokeSubstrate)
        for index in range(0, min(2, CIRCUITS)):
            with SmokeContext(0):
                if tc:
                    tc.test.assertEqual(SmokeContext.require().count, 0)
                self.sub_circuits.append(
                    SmokeSubCircuit(index)
                    @ Placement(
                        (-5, 5 * index),
                        on=Side.Bottom if index else Side.Top,
                    )
                )

                @Design.Initialized.on
                def check():
                    if tc:
                        tc.test.assertEqual(SmokeContext.require().count, 1)

        tc = ContextTest.get()
        if tc:
            tc.test.assertIsNone(SmokeContext.get())

        self.annotate(r"$$L = \frac{1}{2} \rho v^2 S C_L$$")
        self.annotate("Annotation **bold** again 3\nAnd more text")
        self.annotate("""__Advertisement__

- __[jitx](https://app.jitx.com)__ - JITX portal.
- __[jitx docs](https:/docs.jitx.com)__ - JITX Docs
  and more.

You will like making those PCB designs.

---

# h1 Heading
## h2 Heading
### h3 Heading
#### h4 Heading
##### h5 Heading
###### h6 Heading

## Horizontal Rules

___

---

***

## Emphasis

**This is bold text**

__This is bold text__

*This is italic text*

_This is italic text_

~~Strikethrough~~


## Blockquotes


> Blockquotes can also be nested...
>> ...by using additional greater-than signs right next to each other...
> > > ...or with spaces between arrows.


## Lists

Unordered

+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    * Ac tristique libero volutpat at
    + Facilisis in pretium nisl aliquet
    - Nulla volutpat aliquam velit
+ Very easy!

Ordered

1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


1. You can use sequential numbers...
1. ...or keep all the numbers as `1.`

Start numbering with offset:

57. foo
1. bar


## Code

Inline `code`

Indented code

    // Some comments
    line 1 of code
    line 2 of code
    line 3 of code


## Tables

| Option | Description |
| ------ | ----------- |
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

Right aligned columns

| Option | Description |
| ------:| -----------:|
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |


## Links

[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

## Images

![Minion](https://octodex.github.com/images/minion.png)
![Gitlab svg](https://images.ctfassets.net/xz1dnu24egyd/3FbNmZRES38q2Sk2EcoT7a/a290dc207a67cf779fc7c2456b177e9f/press-kit-icon.svg)
![Stormtroopocat](https://octodex.github.com/images/stormtroopocat.jpg "The Stormtroopocat")""")

    @Design.Initialized.on
    def on_initialized(self, initialized):
        components = len(list(extract(DesignContext.require(), SmokeComponent)))
        tc = ContextTest.get()
        if tc:
            tc.test.assertEqual(components, COMPONENTS * CIRCUITS)
            tc.test.assertIsNone(SmokeContext.get())


class GNDTag(Tag):
    pass


class SupplyTag(Tag):
    pass


class CustomTag(Tag):
    pass


class SpecialTag(Tag):
    pass


class SmokeSchematicTemplate(SchematicTemplate):
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


class SmokeDesign(Design):
    board = SmokeBoard()
    substrate = SmokeSubstrate()
    circuit = SmokeMainCircuit()
    schematic_template = SmokeSchematicTemplate()
    paper = Paper.ANSI_B

    def __init__(self):
        self.rules = []
        powerand = GNDTag() & SupplyTag()
        poweror = GNDTag() | SupplyTag()
        powernot = ~poweror
        boolcomplex1 = powernot & CustomTag()
        boolcomplex2 = CustomTag() & powerand

        self.rules.append(
            BinaryDesignRule(
                boolcomplex1, boolcomplex2, name="clearance_0.5"
            ).clearance(0.5)
        )

        self.schematic_markings = []
        self.schematic_markings.append(
            SchematicMarking(
                '<g><text x="-55" y="0" font-family="Arial" font-size="20" fill="black">Smoke test 🔥</text></g>',
                Anchor.S,
            )
        )

        self.schematic_markings.append(
            SchematicMarking(
                '<g><text x="0" y="5" font-family="Arial" font-size="5" fill="black">Hello 😊</text></g>',
                Anchor.NE,
            )
        )

        self.schematic_title_page = SchematicTitlePage(
            """<svg width="279" height="216" viewBox="0 0 279 216" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#2C3E50" />
                        <stop offset="100%" stop-color="#3498DB" />
                    </linearGradient>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <rect x="0" y="0" width="279" height="216" rx="10" fill="url(#bgGradient)" />
                <text x="50" y="110" font-family="Arial, Helvetica, sans-serif" font-size="50" fill="white" filter="url(#glow)" font-weight="bold">JITX</text>
                <text x="180" y="106" font-family="Arial" font-size="40" filter="url(#glow)">🚀</text>
                <line x1="18" y1="140" x2="261" y2="140" stroke="white" stroke-width="2" opacity="0.2" />
                <circle cx="18" cy="140" r="4" fill="white" opacity="0.75" />
                <circle cx="261" cy="140" r="4" fill="white" opacity="0.75" />
            </svg>""",
        )

        # Rule for custom nets
        self.rules.append(
            UnaryDesignRule(CustomTag(), priority=1)
            .trace_width(0.5)
            .stitch_via(SmokeVia, SquareViaStitchGrid(pitch=5.0, inset=0.5))
            .thermal_relief(gap_distance=0.1, spoke_width=0.1, num_spokes=4)
        )

        # Rule for GND nets
        self.rules.append(
            UnaryDesignRule(GNDTag(), priority=2)
            .trace_width(0.3)
            .stitch_via(SmokeVia, TriangularViaStitchGrid(pitch=1.5, inset=1.0))
            .fence_via(
                SmokeVia,
                ViaFencePattern(
                    pitch=1.0,
                    offset=0.5,
                    num_rows=6,
                    # min_pitch=0.1,
                    # max_pitch=1.0,
                    # initial_offset=0.2,
                    # input_shape_only=True,
                ),
            )
            .thermal_relief(gap_distance=1.0, spoke_width=0.25, num_spokes=4)
        )

        # Rules between GND and non-custom nets
        self.rules.append(
            BinaryDesignRule(GNDTag(), ~CustomTag(), priority=0).clearance(0.50)
        )

        self.rules.append(rule(IsPad, IsTrace, priority=0).clearance(0.20))
        self.rules.append(rule(OnLayer(-1)).trace_width(0.05))

        self.rules.append(rule(TrueExpr()).trace_width(0.2))


class RawInstantiableTest(unittest.TestCase):
    def test_raw_design_is_instantiable(self):
        import jitx._structural

        design = SmokeDesign()
        self.assertIsInstance(design, jitx._structural.Instantiable)


@dataclass
class ContextTest(Context):
    test: jitx.test.TestCase


class SmokeTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        ContextTest(self).set()
        design = SmokeDesign()
        self.assertIsInstance(design.circuit, SmokeMainCircuit)

        VerifyEvent(self).fire()

        self.assertEqual(
            tuple(c.name for c in design.substrate.stackup.conductors),
            ("Front Bun", "Lettuce", "Tomato", "Back Bun"),
        )

        import jitx._translate.design

        jitx._translate.design.package_design(design)
