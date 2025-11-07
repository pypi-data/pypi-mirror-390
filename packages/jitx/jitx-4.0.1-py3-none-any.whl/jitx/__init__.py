"""
JITX Python API
===============

The JITX Python API is a set of classes that can be used to build a design in
Python. The core principle of the API is that, when run, your code constructs
an object tree that is then inspected. This means that creating an object and
attaching them to other objects is what drives the construction of the design,
and not function calls. The root of the tree is an instance of a
:py:class:`~jitx.design.Design` subclass. The JITX runtime will inspect your
project looking for Design subclasses which are then instantiated on request.

The inspection mechanism will traverse lists, tuples, and dictionaries, as
well, thus objects can be added to arrays and dictionaries as needed when
building the object tree.

The API is designed to be as simple as possible, and to be as close to Python
as possible. The API is designed to be used with a Python language server, such
as PyLance/pyright, to provide autocompletion and type checking.

.. note::

    There are a few mechanisms designed to make API usage cleaner by allowing
    instantiated objects as class attributes, but there are caveats to be aware
    of when doing more involved logic, and when in doubt, all logic can also be
    placed in the initializer of the class. Runtime errors involving an
    unexpected "Instantiable" object is indicative of this type of error.
"""

from .anchor import Anchor as Anchor
from .board import Board as Board
from .circuit import Circuit as Circuit, CurrentCircuit
from .component import Component as Component, CurrentComponent
from .constraints import (
    AnyObject as AnyObject,
    IsBoardEdge as IsBoardEdge,
    IsCopper as IsCopper,
    IsHole as IsHole,
    IsNeckdown as IsNeckdown,
    IsPad as IsPad,
    IsPour as IsPour,
    IsThroughHole as IsThroughHole,
    IsTrace as IsTrace,
    IsVia as IsVia,
    SquareViaStitchGrid as SquareViaStitchGrid,
    Tag as Tag,
    Tags as Tags,
    TriangularViaStitchGrid as TriangularViaStitchGrid,
    ViaFencePattern as ViaFencePattern,
    design_constraint as design_constraint,
)
from .container import Composite as Composite, Container as Container
from .context import ContextProperty
from .copper import Copper as Copper, Pour as Pour
from .design import Design as Design, DesignContext
from .error import UserCodeException as UserCodeException
from .feature import (
    Courtyard as Courtyard,
    Custom as Custom,
    Cutout as Cutout,
    Finish as Finish,
    Glue as Glue,
    KeepOut as KeepOut,
    Paste as Paste,
    Silkscreen as Silkscreen,
    Soldermask as Soldermask,
)
from .inspect import decompose as decompose, extract as extract, visit as visit
from .landpattern import (
    Landpattern as Landpattern,
    Pad as Pad,
    PadMapping as PadMapping,
)
from .layerindex import LayerSet as LayerSet, Side as Side
from .net import (
    DiffPair as DiffPair,
    Net as Net,
    Port as Port,
    provide as provide,
    Provide as Provide,
)
from .placement import Placement as Placement, Positionable as Positionable
from .shapes.composites import capsule as capsule, rectangle as rectangle
from .shapes.primitive import (
    Arc as Arc,
    ArcPolygon as ArcPolygon,
    ArcPolyline as ArcPolyline,
    Circle as Circle,
    Polygon as Polygon,
    Polyline as Polyline,
)
from .substrate import Substrate as Substrate, SubstrateContext
from .symbol import Pin as Pin, Symbol as Symbol, SymbolMapping as SymbolMapping
from .toleranced import Toleranced as Toleranced
from .transform import Point as Point, Transform as Transform
from .via import Via as Via

# the pattern used above
#
# from X import Class as Class
#
# is a convention to indicate to language servers that the name should be
# reexported from the module and offered during autocompletion, as well as not
# flagged as an unused import.


class Current:
    """
    Context registry object, where each field is a property that will get
    the currently registered context value. If no such context is currently
    active, it will raise an exception. This is purely for convenience, the
    contexts can be accessed directly.

    The main purpose of this is to allow introspection of the environment. Note
    that any accessed context value will be part of the memoization key, and
    thus if the environment changes a memoized element will be reevaluated, and
    thus use of current circuit or component should be used with care.

    There is already an instance of this class, :py:data:`current`, which can
    be used directly.
    """

    design = ContextProperty(DesignContext, lambda x: x.design)
    "The current design being built"
    substrate = ContextProperty(SubstrateContext, lambda x: x.substrate)
    "The substrate of the current design"
    circuit = ContextProperty(CurrentCircuit, lambda x: x.circuit)
    "The current circuit being constructed"
    component = ContextProperty(CurrentComponent, lambda x: x.component)
    "The current component being constructed"

    def __repr__(self):
        return "Current"


current = Current()
"""Singleton, the "current" context registry."""

# this can't be autogenerated at runtime, since the typechecker won't know what is
# actually imported if someone does from jitx import *, thus they need to be
# listed in the source file; please remember to update this if you add new
# imports that should be reexported

# grep '^\(from\|   \)' __init__.py | grep -o 'as [^, ]*\(,\|$\)' | sed -e 's/^as \([^,]*\).*$/    "\1",/'
__all__ = [
    "current",
    # list below is generated with the grep command
    "Anchor",
    "Board",
    "Circuit",
    "Component",
    "IsBoardEdge",
    "IsCopper",
    "IsHole",
    "IsNeckdown",
    "IsPad",
    "IsPour",
    "IsThroughHole",
    "IsTrace",
    "IsVia",
    "SquareViaStitchGrid",
    "Tag",
    "Tags",
    "TriangularViaStitchGrid",
    "ViaFencePattern",
    "design_constraint",
    "Composite",
    "Container",
    "Copper",
    "Pour",
    "Design",
    "UserCodeException",
    "Courtyard",
    "Custom",
    "Cutout",
    "Finish",
    "Glue",
    "KeepOut",
    "Paste",
    "Silkscreen",
    "Soldermask",
    "decompose",
    "extract",
    "visit",
    "Landpattern",
    "Pad",
    "PadMapping",
    "LayerSet",
    "Side",
    "DiffPair",
    "Net",
    "Port",
    "provide",
    "Provide",
    "Placement",
    "Positionable",
    "capsule",
    "rectangle",
    "Arc",
    "ArcPolygon",
    "ArcPolyline",
    "Circle",
    "Polygon",
    "Polyline",
    "Substrate",
    "Pin",
    "Symbol",
    "SymbolMapping",
    "Toleranced",
    "Point",
    "Transform",
    "Via",
]
