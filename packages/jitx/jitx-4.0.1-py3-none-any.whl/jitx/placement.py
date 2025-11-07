"""
Component placement and positioning
===================================

This module provides classes for positioning components and other objects
on the board with transformations and side placement.
"""

from __future__ import annotations

from typing import cast, overload, Self

from .transform import Transform, Point
from .layerindex import Side
from ._structural import Proxy, Structural


class Placement(Transform):
    """Component placement with side information.

    Extends Transform to include which side of the board the component is placed on.
    """

    side: Side = Side.Top
    """Which side of the board this placement is on."""

    @overload
    def __init__(
        self, xform: Point | Transform | Placement, /, *, on: Side | None = None
    ): ...
    @overload
    def __init__(
        self,
        translate: Point,
        rotate: float = 0,
        scale: float | tuple[float, float] = (1, 1),
    ): ...

    def __init__(
        self,
        translate: Point | Transform | Placement,
        rotate: float = 0,
        scale: float | tuple[float, float] = (1, 1),
        *,
        on: Side | None = None,
    ):
        """Initialize a placement.

        Args:
            xform: Transform, point, or existing placement to adopt.
            on: Which side to place on.
        """
        if isinstance(translate, Transform):
            xform = translate
            super().__init__(xform._translate, xform._rotate, xform._scale)
            side = on or Side.Top
            if isinstance(xform, Placement):
                side = side * xform.side
            self.side = on or side
        else:
            super().__init__(translate, rotate, scale)
            self.side = on or Side.Top

    def __repr__(self):
        return f"Placement({super().__repr__()}, {self.side})"

    def _post_mul(self, left: Transform, right: Transform):
        left = cast(Placement, left)  # otherwise we wouldn't be here
        side = left.side
        if isinstance(right, Placement):
            side = side * right.side
        self.side = side
        return self

    def _post_rmul(self, result: Transform, left: Transform):
        # not called if left was a Placement, no need to check its side
        return Placement(result, on=self.side)


class Kinematic[T: Transform]:
    """Mixin for objects that can have transforms applied."""

    transform: T | None = None
    """The transform applied to this object."""


class Positionable(Structural, Kinematic[Placement]):
    """Base class for objects that can be positioned on the board."""

    def __matmul__(self, where: Point | Transform | Placement) -> Self:
        # FIXME implement proxy handling for everything in translation
        # return Proxy.create(self).at(where)
        return self.at(where)

    @overload
    def at(
        self, point: Point, /, *, on: Side = Side.Top, rotate: float = 0
    ) -> Self: ...

    @overload
    def at(self, xform: Transform | Placement, /, *, on: Side = Side.Top) -> Self: ...

    @overload
    def at(
        self, x: float, y: float, /, *, on: Side = Side.Top, rotate: float = 0
    ) -> Self: ...

    def at(
        self,
        x: Placement | Transform | Point | float,
        y: float | None = None,
        /,
        *,
        on: Side = Side.Top,
        rotate: float = 0,
    ):
        """Place this object relative to its frame of reference. Note that this
        modifies the object, and does not create a copy.

        Args:
            x: x-value, transform, or placement to adopt.
            y: y-value if x is an x-value. This argument is only valid in that context.
            rotate: Rotation in degrees to apply to the object. Only applicable
                if not supplying a transform or placement.
            on: If set to bottom, this object will be placed on the "opposite"
                side from its frame of reference. This means if the frame of
                reference is on the bottom of the board, setting this to "bottom"
                will actually put the object back on top.
        Returns:
            the object itself."""
        if isinstance(x, Placement | Transform | tuple):
            assert y is None
            placement = Placement(x, on=on)
            placement._rotate += rotate
        else:
            assert isinstance(y, float | int)
            placement = Placement((x, y), on=on)
            placement._rotate += rotate
        if isinstance(self, Proxy):
            # setting the transform does not taint the proxy.
            with Proxy.override():
                self.transform = placement
        else:
            self.transform = placement
        return self
