"""
Schematic Symbols
=================

This module provides classes for defining schematic symbols, pins,
and symbol mappings for components. You attach a symbol to a component by
assigning it to a member field. The name of the field is not important, and
multiple symbols can be attached to the same component to provide multiple
symbol units.
"""

from __future__ import annotations
from collections.abc import Iterable, Mapping, Sequence
from enum import Enum

from .memo import memoize
from .net import Port

from ._structural import Ref, Structural
from .transform import GridPoint


@memoize
class Symbol(Structural):
    """Symbols are a structural element in JITX encoding the schematic
    representation of a part. Symbols often contain electrical connection points
    represented by :py:class:`~jitx.symbol.Pin`, geometric artwork, and
    :py:class:`~jitx.shapes.primitive.Text` annotations. Symbols are linked to a
    design through a :py:class:`~jitx.component.Component` where a symbol's
    :py:class:`~jitx.symbol.Pin` objects are mapped to :py:class:`~jitx.net.Port` objects.

    Valid elements in a symbol are:
        - :py:class:`~jitx.shapes.Shape`
        - :py:class:`~jitx.symbol.Pin`
        - :py:class:`~jitx.symbol.SymbolOrientation`
        - :py:class:`~jitx.symbol.Symbol`

    If a symbol is defined inside another symbol, they will be treated
    together as one symbol in the design.

    For a rectangular symbol with automatic or configurable pin layout,
    use :py:class:`~jitxlib.symbols.box.BoxSymbol`.

    >>> class MySymbol(Symbol):
    ...     a = Pin(at=(1, 0), length=1, direction=Direction.Right)
    ...     b = Pin(at=(-1, 0), length=1, direction=Direction.Left)
    ...     pin_name_size = 0.3
    ...     pad_name_size = 0.3
    ...     orientation = SymbolOrientation(0)
    ...     rect = rectangle(2, 2)

    >>> class MyComponent(Component):
    ...     ports = [Port() for _ in range(2)]
    ...     symbol = BoxSymbol()
    """

    pin_name_size: float | None = None
    """
    Font size of pin name text of :py:class:`~jitx.symbol.Pin` objects in this symbol, in grid units.
    If unset, defers to a parent :py:class:`~jitx.symbol.Symbol`, if a parent exists.
    This can be overriden at the :py:class:`~jitx.symbol.Pin` level by setting its :py:attr:`~jitx.symbol.Symbol.pin_name_size` attribute.
    """
    pad_name_size: float | None = None
    """
    Font size of pad name text of :py:class:`~jitx.symbol.Pin` objects in this symbol, in grid units.
    If unset, defers to a parent :py:class:`~jitx.symbol.Symbol`, if a parent exists.
    This can be overriden at the :py:class:`~jitx.symbol.Pin` level by setting its :py:attr:`~jitx.symbol.Symbol.pad_name_size` attribute.
    """


class Direction(Enum):
    """Pin direction on schematic symbols."""

    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"


class Pin(Structural):
    """Schematic symbol pin definition."""

    at: GridPoint
    "The position of the pin in grid units."
    length: int = 0
    "The length of the pin in grid units."
    direction: Direction = Direction.Left
    "The direction of the pin."
    pin_name_size: float | None = None
    """
    Font size of the pin's pin name text in grid units, overriding the parent
    :py:class:`~jitx.symbol.Symbol`'s :py:attr:`~jitx.symbol.Symbol.pin_name_size` attribute.
    """
    pad_name_size: float | None = None
    """
    Font size of the pin's pad name text in grid units, overriding the parent
    :py:class:`~jitx.symbol.Symbol`'s :py:attr:`~jitx.symbol.Symbol.pad_name_size` attribute.
    """

    def __init__(
        self,
        at: GridPoint,
        length: int = 0,
        direction: Direction = Direction.Left,
        pin_name_size: float | None = None,
        pad_name_size: float | None = None,
    ):
        """Initialize a schematic pin.

        Args:
            at: Position of the pin in grid units.
            length: Length of the pin in grid units.
            direction: Direction the pin points.
            pin_name_size: Font size for pin name text.
            pad_name_size: Font size for pad name text.
        """
        self.at = at
        self.length = length
        self.direction = direction
        self.pin_name_size = pin_name_size
        self.pad_name_size = pad_name_size

    def __repr__(self):
        return f"Pin(at={self.at}, length={self.length}, direction={self.direction})"


class SymbolMapping(Structural, Ref):
    """Mapping between component ports and schematic symbol pins.

    If no symbol mapping is provided, a default mapping will be created that maps ports to symbol pins in declaration order.


    >>> class MyComponent(Component):
    ...     GND = Power()
    ...     VIN = Power()
    ...     VOUT = Power()
    ...
    ...     symbol = MySymbol()
    ...     mappings = SymbolMapping({
    ...         GND: symbol.gnd,
    ...         VIN: symbol.vin,
    ...         VOUT: symbol.vout,
    ...     })
    """

    __entries: dict[Port, Pin]

    def __init__(self, entries: Mapping[Port, Pin] | Iterable[tuple[Port, Pin]]):
        """Initialize a symbol mapping.

        Args:
            entries: Mapping or iterable of (port, pin) pairs.
        """
        self.__entries = dict(entries)

    def __setitem__(self, port: Port, pin: Pin):
        self.__entries[port] = pin

    def __getitem__(self, port: Port):
        return self.__entries[port]

    def __iter__(self):
        return iter(self.__entries)

    def items(self):
        return self.__entries.items()

    def values(self):
        return self.__entries.values()


class SymbolOrientation:
    """Permitted orientations for a schematic symbol.

    In initial placement of schematic symbols, the engine may rotate the symbol
    to be in any of the permitted orientations. If no orientations are specified,
    then all orientations are permitted.
    """

    rotations: list[int]
    """List of allowed rotation angles in degrees."""

    def __init__(self, rotations: Sequence[int] | int = ()):
        """Initialize symbol orientation constraints.

        Args:
            rotations: Allowed rotation angles in degrees (must be multiples of 90).

        Raises:
            ValueError: If rotation is not a multiple of 90 degrees.
        """
        if isinstance(rotations, int):
            rotations = [rotations]

        # Normalize rotations to 0-359 range and validate they're multiples of 90
        normalized_rotations = []
        for r in rotations:
            normalized = r % 360
            if normalized % 90 != 0:
                raise ValueError(
                    f"Invalid symbol orientation: {r}. Rotation must be a multiple of 90 degrees"
                )
            normalized_rotations.append(normalized)

        # Use sorted set to automatically handle ordering and deduplication
        self.rotations = sorted(set(normalized_rotations))


# no export
del Structural
# ruff doesn't like deleting things that weren't used as base classes?
# del GridPoint
