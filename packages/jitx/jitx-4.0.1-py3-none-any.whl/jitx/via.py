"""
Via definitions
===============

This module provides classes for defining vias, including via types,
backdrill specifications, and via properties.
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from .layerindex import Side
from .placement import Positionable

if TYPE_CHECKING:
    from jitx.si import PinModel


class Via(Positionable):
    """Via definition that can be instantiated in the board.
    Layer indexes referenced in this definition are absolute in the board: 0 is always the top layer.
    They are not relative to any component / circuit. Flipping via instances in the UI will not flip those layers,
    contrary to landpattern pads.

    >>> class StandardVia(Via):
    ...     start = Side.Top
    ...     stop = Side.Bottom
    ...     diameter = 0.6
    ...     diameters = {0: 0.5, 1: ViaDiameter(0.5, nfp=0.2)}
    ...     hole_diameter = 0.3
    ...     type = ViaType.MechanicalDrill
    """

    type: ClassVar[ViaType]
    """Type of via drilling method: MechanicalDrill or LaserDrill."""
    start_layer: ClassVar[int]
    """Starting layer for the via. Setting this to a layer index other than the top layer allows for creating buried or blind vias."""
    stop_layer: ClassVar[int]
    """Ending layer for the via."""
    diameter: ClassVar[float | ViaDiameter]
    """Pad diameter of the via, in mm. Can be overridden on a per-layer basis by :py:attr:`~jitx.via.Via.diameters`."""
    diameters: dict[int | tuple[int, ...], float | ViaDiameter] = {}
    """Pad diameters of the via for specific layers. Overrides :py:attr:`~jitx.via.Via.diameter` for the given layers."""
    hole_diameter: ClassVar[float]
    """Drilled or laser-cut hole diameter for the via, in mm."""
    filled: ClassVar[bool] = False
    """Whether the via is filled."""
    tented: ClassVar[set[Side] | Side | None | bool] = True
    """Whether the via is tented on Top, Bottom, or both sides. Untented sides will have a solder mask opening."""
    via_in_pad: ClassVar[bool] = False
    """Whether the via is allowed to be placed inside a component's pads."""
    backdrill: ClassVar[BackdrillSet | Backdrill | None] = None
    """Backdrill specifications. If a :py:class:`Backdrill` is used, it will be
    assumed to be drilled from bottom."""
    models: ClassVar[dict[tuple[int, int], PinModel]] = {}
    """Specifies delay and loss models for the via."""


class ViaDiameter:
    """Diameters of various features of a via."""

    pad: float
    """Pad diameter for the via, in mm."""
    nfp: float | None = None
    """Pad diameter for the via when non-functional pads are removed, in mm.
    When provided, it overrides the pad diameter except on the start layer if there is no top backdrill,
    stop layer if there is no bottom backdrill and intermediate copper layers that have traces or pours connected to the via."""

    def __init__(
        self,
        pad: float,
        *,
        nfp: float | None = None,
    ):
        self.pad = pad
        self.nfp = nfp


class ViaType(Enum):
    """Type of via drilling method."""

    MechanicalDrill = 1
    LaserDrill = 2


@dataclass
class Backdrill:
    """Backdrill specification for a via."""

    diameter: float
    """Diameter of the backdrill in mm."""
    startpad_diameter: float
    """Diameter of the starting pad in mm."""
    solder_mask_opening: float
    """Solder mask opening size in mm."""
    copper_clearance: float
    """Copper clearance diameter in mm."""


@dataclass
class BackdrillSet:
    """Set of backdrill specifications for top and bottom sides."""

    top: Backdrill | None = None
    """Backdrill specification for the top side."""
    bottom: Backdrill | None = None
    """Backdrill specification for the bottom side."""
