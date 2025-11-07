"""
Landpattern and Pad definitions
===============================

This module provides classes for defining component landpatterns,
pads, and mappings between ports and pads.
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence, Mapping
from typing import overload

from .net import Port
from .shapes import Shape
from .placement import Positionable
from .memo import memoize
from ._structural import Ref, Structural


@memoize
class Landpattern(Positionable):
    """Component landpattern definition, also known as a footprint, package, or land-pattern.

    Defines the pads and associated geometry for the interface between an electrical component and the circuit board.

    >>> class ZigZagLandpattern(Landpattern):
    ...     pad1 = MyPad().at(-0.5, 0)
    ...     pad2 = MyPad().at(0.5, 0)
    ...
    ...     silkscreen = Silkscreen(
    ...         Polyline(
    ...             0.1,
    ...             [
    ...                 (-0.4, 1), (-0.3, 1.2), (-0.2, 0.8),
    ...                 (-0.1, 1.2), (0, 0.8), (0.1, 1.2),
    ...                 (0.2, 0.8), (0.3, 1.2), (0.4, 1),
    ...             ]
    ...         )
    ...     )
    ...
    ...     courtyard = Courtyard(rectangle(2, 1))
    """

    pass


class PadShape:
    """Shapes of various features of a pad."""

    shape: Shape
    """The geometric shape of the pad."""
    nfp: Shape | None = None
    """The geometric shape of the pad when non-functional pads are removed.
    When provided, it overrides the pad shape except on the top layer, bottom layer
    and intermediate copper layers that have traces or pours connected to the pad."""

    def __init__(
        self,
        shape: Shape,
        *,
        nfp: Shape | None = None,
    ):
        self.shape = shape
        self.nfp = nfp


@memoize
class Pad(Positionable):
    """Class representing a pad, user code should overload this class in order
    to create new pad definitions. If the pad contains a
    :py:class:`~jitx.feature.Cutout` it will be interpreted as a through-hole
    pad, otherwise it will be interpreted as a surface mount pad.

    >>> class MyPad(Pad):
    ...     shape = Circle(diameter=0.8)
    ...     shapes = {
    ...         (0, 2): Circle(diameter=0.7),
    ...         1: PadShape(Circle(diameter=0.8), nfp=Circle(diameter=0.4)),
    ...         -1: rectangle(2., 2.),
    ...     }
    ...
    ...     def __init__(self):
    ...         self.cutout = Cutout(Circle(diameter=0.4)
    ...         self.soldermask = Soldermask(self.shape)
    """

    shape: Shape | PadShape
    """The geometric shape of the pad or a PadShape to specify the regular shape and the shape when non-functional pads are removed.
    Can be overridden on a per-layer basis by :py:attr:`~jitx.landpattern.Pad.shapes`."""
    shapes: dict[int | tuple[int, ...], Shape | PadShape] = {}
    """The geometric shapes of the pad for specific layers. Overrides :py:attr:`~jitx.landpattern.Pad.shape` for the given layers."""


class PadMapping(Structural, Ref):
    """Mapping between component ports and landpattern pads.

    If no pad mapping is provided, a default mapping will be created that maps ports to pads in declaration order.
    If a port needs to be mapped to multiple pads, a PadMapping is required.


    >>> class MyComponent(Component):
    ...     GND = Power()
    ...     VIN = Power()
    ...     VOUT = Power()
    ...
    ...     lp = MyLandpattern()
    ...     mappings = PadMapping({
    ...         GND: [lp.p[1], lp.p[4]],
    ...         VIN: lp.p[3],
    ...         VOUT: lp.p[3],
    ...     })

    >>> class MyComponent(Component):
    ...     GND = Power()
    ...     VIN = Power()
    ...     VOUT = Power()
    ...
    ...     lp = MyLandpattern()
    ...     mappings = PadMapping({
    ...         GND: lp.p[1],
    ...         VIN: lp.p[2],
    ...         VOUT: lp.p[3],
    ...     })
    """

    __entries: dict[Port, Pad | Sequence[Pad]]
    __inverse: dict[Pad, Port]

    def __init__(
        self,
        entries: Mapping[Port, Pad | Sequence[Pad]]
        | Iterable[tuple[Port, Pad | Sequence[Pad]]],
    ):
        """Initialize a pad mapping.

        Args:
            entries: Mapping or iterable of (port, pad) or (port, pad sequence) pairs.
        """
        self.__entries = dict(entries)
        self.__inverse = {}
        for port, pad in self.__entries.items():
            if isinstance(pad, Sequence):
                for p in pad:
                    self.__inverse[p] = port
            else:
                self.__inverse[pad] = port

    @overload
    def __setitem__(self, port: Port, pad: Pad | Sequence[Pad], /): ...
    @overload
    def __setitem__(self, pad: Pad, port: Port, /): ...
    def __setitem__(self, port: Port | Pad, pad: Port | Pad | Sequence[Pad]):
        if isinstance(port, Pad):
            assert isinstance(pad, Port)
            other = self.__entries.get(pad)
            if isinstance(other, Sequence):
                self.__entries[pad] = tuple(other) + (port,)
            elif isinstance(other, Pad):
                self.__entries[pad] = (port, other)
            else:
                self.__entries[pad] = port
            self.__inverse[port] = pad
        elif isinstance(pad, Sequence):
            self.__entries[port] = pad
            for p in pad:
                self.__inverse[p] = port
        else:
            assert isinstance(pad, Pad)
            self.__entries[port] = pad
            self.__inverse[pad] = port

    @overload
    def __getitem__(self, port: Port) -> Pad | Sequence[Pad]: ...
    @overload
    def __getitem__(self, port: Pad) -> Port: ...
    def __getitem__(self, port: Port | Pad):
        if isinstance(port, Pad):
            return self.__inverse[port]
        return self.__entries[port]

    @overload
    def get[T](
        self, port: Port, default: T = None, /
    ) -> Pad | Sequence[Pad] | Port | T: ...
    @overload
    def get[T](self, port: Pad, default: T = None, /) -> Port | T: ...
    def get[T](
        self, port: Port | Pad, default: T = None, /
    ) -> Pad | Sequence[Pad] | Port | T:
        """Return the pad or port associated with the given port or pad."""
        if isinstance(port, Pad):
            return self.__inverse.get(port, default)
        return self.__entries.get(port, default)

    def __contains__(self, port: Port | Pad):
        if isinstance(port, Pad):
            return port in self.__inverse
        return port in self.__entries

    def __len__(self):
        return len(self.__entries)

    def __iter__(self):
        return iter(self.__entries)

    def items(self):
        return self.__entries.items()

    def values(self):
        return self.__entries.values()

    def inverse(self) -> Mapping[Pad, Port]:
        """Return the inverse mapping from pads to ports."""
        return self.__inverse
