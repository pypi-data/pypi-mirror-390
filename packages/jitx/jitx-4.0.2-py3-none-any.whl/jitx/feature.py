"""
Feature definitions
===================

This module provides feature classes for representing board elements
like cutouts, keepouts, silkscreen, and other board features. Notably, this
does not include copper shapes, see the :py:mod:`~jitx.copper` module for that.
"""

from dataclasses import dataclass, replace
from typing import Self
import os
import warnings

# using fq names here to prevent reexport
import jitx._structural
import jitx.shapes
import jitx.layerindex


_warn_skips = (os.path.dirname(__file__),)


@dataclass
class Feature(jitx._structural.Critical):
    """Base class for board features."""

    shape: jitx.shapes.Shape
    """Shape of this feature."""

    def invert(self) -> Self:
        """Return a copy of this feature with the layers inverted."""
        return replace(self)


@dataclass
class Cutout(Feature):
    """Cutout element for holes and slots. Through-hole pads will include their
    hole definition using a Cutout.

    >>> cutout = Cutout(Circle(radius=1.0))
    """


@dataclass
class MultiLayerFeature(Feature):
    """Feature that spans multiple board layers."""

    layers: jitx.layerindex.LayerSet
    """The set of layers this feature applies to."""

    def invert(self) -> Self:
        return replace(self, layers=self.layers.invert())


@dataclass(kw_only=True)
class KeepOut(MultiLayerFeature):
    """Construct keepout regions on a range of layers.

    >>> # Keep out pours and vias on the top layer
    >>> keepout = KeepOut(layers=LayerSet(0), pour=True, via=True, route=False)
    """

    pour: bool = False
    """Keep pours from covering this area."""
    via: bool = False
    """Avoid auto-placing vias in this area."""
    route: bool = False
    """Disallow auto-router traces in this area."""

    def __post_init__(self):
        if not (self.pour or self.via or self.route):
            warnings.warn(
                "KeepOut has no effect: all of pour, via, and route are False. "
                "Set at least one to True for the keepout to have any effect.",
                skip_file_prefixes=_warn_skips,
                stacklevel=2,
            )


# @dataclass
# class BoardEdge(Feature):
#     """Board edge alignment feature."""


@dataclass
class SurfaceFeature(Feature):
    """Surface features are features that apply to either top or bottom side of
    the board, but not to internal layers. This class should not be used
    directly, instead use one of the subclasses."""

    side: jitx.layerindex.Side = jitx.layerindex.Side.Top
    """Side of this surface feature. Note that a "bottom" side simply means the
    opposite side of where the landpattern / module it's associated with is
    placed, and not necessarily the bottom side."""

    def invert(self) -> Self:
        return replace(self, side=self.side.flip())


@dataclass
class Silkscreen(SurfaceFeature):
    """Add a shape to the silkscreen layer

    >>> silkscreen = Silkscreen(rectangle(2, 3), side=Side.Bottom)
    """


@dataclass
class Soldermask(SurfaceFeature):
    """Add a shape to the solder mask layer

    >>> soldermask = Soldermask(rectangle(2, 1), side=Side.Top)
    """


@dataclass
class Paste(SurfaceFeature):
    """Add a shape to the paste application layer

    >>> paste = Paste(circle(diameter=1))
    """


@dataclass
class Glue(SurfaceFeature):
    """Add a shape to the glue application layer

    >>> glue = Glue(circle(diameter=1), side=Side.Bottom)
    """


@dataclass
class Finish(SurfaceFeature):
    """Add a shape to the glue application layer

    >>> finish = Finish(rectangle(1, 1))
    """


@dataclass
class Courtyard(SurfaceFeature):
    """Courtyards are used to indicate land pattern bounds.

    >>> courtyard = Courtyard(rectangle(3, 3))
    """

    def __post_init__(self):
        # lines forming a rectangle are often erroneously used to represent a
        # rectangular courtyard, trap it here and have them convert it to a
        # polygon if they really want to keep it.
        from jitx.shapes.primitive import Polyline, ArcPolyline

        if isinstance(self.shape.geometry, Polyline | ArcPolyline):
            raise ValueError(
                "Courtyard must be a closed shape, but got a polyline "
                "which is unlikely to actually represent the courtyard shape. "
                "To keep using this shape, convert it to a polygon."
            )


@dataclass(kw_only=True)
class Custom(SurfaceFeature):
    """Custom surface feature with user-defined name.

    >>> custom = Custom(rectangle(2, 2), name="Fab")
    """

    name: str
    """Name of the custom feature layer."""
