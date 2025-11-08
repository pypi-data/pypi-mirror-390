"""
Layer indexing and side definitions
===================================

This module provides classes for representing board sides and layer sets
for specifying which layers features apply to.
"""

from __future__ import annotations
from enum import IntEnum
from collections.abc import Sequence, Iterable
from typing import overload


class Side(IntEnum):
    """Board side enumeration.

    Represents the top and bottom sides of a circuit board.
    """

    Top = 0
    Bottom = -1

    def flip(self):
        """Return the opposite side. Top becomes Bottom, Bottom becomes Top."""
        return Side.Top if self == self.Bottom else Side.Bottom

    def __mul__(self, other):
        """Multiplying another side flips it if this is a Bottom side."""
        if isinstance(other, Side):
            if self == Side.Bottom:
                return other.flip()
            else:
                return other
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, int):
            return self.value + other
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, int):
            return self.value - other
        return NotImplemented

    def __invert__(self):
        """Return the opposite side (same as :py:func:`~jitx.layerindex.Side.flip`)."""
        return self.flip()


type Layers = int | Sequence[int] | LayerSet


class LayerSet:
    """Set of board layers specified by ranges.

    Defines which layers a feature or element applies to using
    layer index ranges.

    Basic construction with individual layers:

    >>> # Single layer
    >>> top_layer = LayerSet(0)
    >>> top_layer.ranges
    [(0, 0)]

    >>> # Multiple individual layers
    >>> signal_layers = LayerSet(0, 2, 4)
    >>> signal_layers.ranges
    [(0, 0), (2, 2), (4, 4)]

    >>> # From a sequence of layers
    >>> power_layers = LayerSet([1, 3, 5])
    >>> power_layers.ranges
    [(1, 1), (3, 3), (5, 5)]

    Range construction using class methods:

    >>> # Range from start to end (exclusive)
    >>> inner_layers = LayerSet.range(1, to=4)
    >>> inner_layers.ranges
    ((1, 3),)

    >>> # Range from start through end (inclusive)
    >>> outer_layers = LayerSet.range(0, through=2)
    >>> outer_layers.ranges
    ((0, 2),)

    >>> # All layers
    >>> all_layers = LayerSet.all()
    >>> all_layers.ranges
    ((0, -1),)

    Combining multiple LayerSet objects:

    >>> # Combine different layer sets
    >>> top_and_bottom = LayerSet(0, -1)
    >>> inner_range = LayerSet.range(1, to=3)
    >>> combined = LayerSet(top_and_bottom, inner_range)
    >>> combined.ranges
    [(0, 0), (-1, -1), (1, 2)]

    Using with explicit ranges:

    >>> # Direct range specification
    >>> custom_ranges = LayerSet(ranges=[(0, 2), (4, 6)])
    >>> custom_ranges.ranges
    [(0, 2), (4, 6)]

    Common use cases:

    >>> # Keepout layers
    >>> keepout = KeepOut(layers=LayerSet(1), pour=False, via=True, route=True)
    """

    ranges: Sequence[tuple[int, int]]
    """Sequence of (start, end) layer index ranges."""

    @overload
    def __init__(self, *layers: Layers): ...
    @overload
    def __init__(self, *, ranges: Sequence[tuple[int, int]] = ()): ...

    def __init__(self, *layers: Layers, ranges: Sequence[tuple[int, int]] = ()):
        """Initialize a layer set.

        Args:
            *range: Layer indices or ranges (inclusive).
        """

        def entries(x: Layers) -> Iterable[tuple[int, int]]:
            if isinstance(x, int):
                return ((x, x),)
            elif isinstance(x, Sequence):
                return ((x, x) for x in x)
            elif isinstance(x, LayerSet):
                return x.ranges
            else:
                raise TypeError(f"Invalid layer entry type: {type(x)}")

        if ranges:
            if layers:
                raise TypeError(
                    "Invalid overload: Called with both 'layers' and 'ranges'"
                )
            self.ranges = ranges
        else:
            self.ranges = [entry for layer in layers for entry in entries(layer)]

    def invert(self) -> LayerSet:
        """Return a layer set with all layers inverted."""
        return LayerSet(ranges=[(-end - 1, -start - 1) for start, end in self.ranges])

    @overload
    @classmethod
    def range(cls, start: int, *, to: int) -> LayerSet: ...
    @overload
    @classmethod
    def range(cls, start: int, *, through: int) -> LayerSet: ...
    @classmethod
    def range(
        cls, start: int, *, to: int | None = None, through: int | None = None
    ) -> LayerSet:
        """Create a layer set from a start and end layer.

        Args:
            start: Starting layer index.
            to: Ending layer index (exclusive).
            through: Ending layer index (inclusive).

        Returns:
            LayerSet covering the specified range.
        """
        if to is not None and through is not None:
            raise ValueError("Cannot specify both 'to' and 'through'")

        # Verbosely written to ensure 'end' is typed as int
        if to is not None:
            end = to - 1
        elif through is not None:
            end = through
        else:
            raise TypeError("Missing argument 'to' or 'through'")

        return LayerSet(ranges=((start, end),))

    @classmethod
    def all(cls) -> LayerSet:
        """Create a layer set covering all layers.

        Returns:
            LayerSet covering all layers from 0 to -1 (bottom).
        """
        return LayerSet(ranges=((0, -1),))
