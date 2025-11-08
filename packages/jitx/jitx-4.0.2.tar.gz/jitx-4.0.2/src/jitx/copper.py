"""
Copper and Pour construction
============================

This module provides classes for representing copper shapes and pours on board
layers.
"""

from __future__ import annotations

import jitx.layerindex
import jitx.shapes
import jitx.net
from jitx._structural import Structural


class Copper(Structural):
    """Copper element on a layer index.

    Represents a copper element with a defined shape on a particular layer index.
    Can be combined with other copper elements to form nets.

    >>> copper = Copper(Circle(diameter=2.0), layer=0)
    """

    shape: jitx.shapes.Shape
    """The geometric shape of the copper element."""
    layer: int
    """The layer index for this copper element."""

    def __init__(self, shape: jitx.shapes.Shape, layer: int):
        """Initialize a copper element.

        Args:
            shape: The geometric shape of the copper.
            layer: The layer index.
        """
        self.shape = shape
        self.layer = layer

    def __add__(self, other: Copper):
        """Combine this copper with another to form a net."""
        return jitx.net.Net([self, other])


class Pour(Copper):
    """Copper pour is a filled copper element with isolation and priority settings.

    >>> self.gnd = Net()
    >>> self.gnd += Pour(Circle(diameter=10.0), layer=0, rank=1)
    """

    isolate: float
    """Isolation distance from other features in millimeters."""
    rank: int = 0
    """Pour priority rank with higher ranks being prioritized."""
    orphans: bool = True
    """Whether to include orphaned copper areas."""

    def __init__(
        self,
        shape: jitx.shapes.Shape,
        layer: int,
        *,
        isolate: float = 0,
        rank: int = 0,
        orphans: bool = True,
    ):
        """Initialize a copper pour.

        Args:
            layer: The layer index.
            shape: The area to fill with copper.
            isolate: Optional isolation distance from other features in
                millimeters. This is a minimum distance, and may be increased to
                meet other design rules.
            rank: Pour priority rank with higher ranks being prioritized.
            orphans: Whether to include orphaned copper areas.
        """
        super().__init__(shape, layer)
        self.isolate = isolate
        self.rank = rank
        self.orphans = orphans
