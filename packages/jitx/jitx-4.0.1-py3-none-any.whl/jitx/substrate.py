"""
Substrate definitions and fabrication constraints
=================================================

This module provides classes for defining substrates with routing structures
and fabrication constraints for manufacturing.
"""

from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from jitx._structural import Critical, Structural
from jitx.decorators import early
from jitx.context import Context
from jitx.inspect import decompose
from jitx.stackup import Stackup
from jitx.si import DifferentialRoutingStructure, RoutingStructure
from jitx.toleranced import Toleranced
from jitx.units import PlainQuantity, ohm


class _HasImpedance(Protocol):
    impedance: PlainQuantity


def _lookup_closest[T: _HasImpedance](
    impedance: float | Toleranced | PlainQuantity, structures: Iterable[T]
) -> T:
    """Look up the closest routing structure for a given impedance.

    Args:
        impedance: Target impedance value.
        structures: Mapping of impedance values to routing structures.

    Returns:
        The closest matching routing structure.

    Raises:
        ValueError: If no applicable routing structure is found.
    """
    if isinstance(impedance, PlainQuantity):
        search = ohm.m_from(impedance)
    else:
        search = impedance
    search = Toleranced.exact(search)
    selected = min(
        (
            struc
            for struc in structures
            if search.in_range(ohm.m_from(struc.impedance, strict=False))
        ),
        key=lambda struc: abs(ohm.m_from(struc.impedance) - search.typ),
        default=None,
    )
    if selected:
        return selected
    raise ValueError(f"No applicable routing structure found for {impedance} Ohms")


class Substrate(Structural, early=True):
    """Substrate definition with routing structures and fabrication constraints.

    Substrates can be equipped with routing and differential routing structures
    which will be introspected when an attempt to lookup a particular impedance
    is made.

    A substrate should also contain the permissible :py:class:`Via` types as
    well as the :py:class:`FabricationConstraints`.

    >>> class MySubstrate(Substrate):
    ...     constraints = MyFabricationConstraints()
    ...
    ...     class THVia(Via):
    ...         start_layer = 0
    ...         stop_layer = 1
    ...         diameter = 0.45
    ...         hole_diameter = 0.3
    ...         type = ViaType.MechanicalDrill
    ...
    ...     RS_50 = RoutingStructure(symmetric_routing_layers(
    ...         name="RS_50",
    ...         impedance=50 * ohm,
    ...         layers=symmetric_routing_layers({
    ...             0: RoutingLayer(
    ...                 trace_width=0.1176,
    ...                 clearance=0.2,
    ...                 velocity=191335235228,
    ...                 insertion_loss=0.0178,
    ...             )
    ...         })
    ...     )

    >>> MySubstrate().routing_structure(50 * ohm)
    RoutingStructure(name="RS_50", impedance=50 Ω)
    """

    stackup: Stackup
    constraints: FabricationConstraints

    @early
    def __setup(self):
        SubstrateContext(self).set()

    def routing_structure(
        self, impedance: Toleranced | PlainQuantity | float
    ) -> RoutingStructure:
        """
        Look up a routing structure for a given impedance. The default
        implementation introspects the substrate for
        :py:class:`RoutingStructure` objects. Override this method if you need
        to implement a custom lookup mechanism.
        """
        return _lookup_closest(impedance, decompose(self, RoutingStructure))

    def differential_routing_structure(
        self, impedance: Toleranced | float
    ) -> DifferentialRoutingStructure:
        """
        Look up a differential routing structure for a given impedance. The
        default implementation introspects the substrate for
        :py:class:`RoutingStructure` objects. Override this method if you need
        to implement a custom lookup mechanism.
        """
        return _lookup_closest(impedance, decompose(self, DifferentialRoutingStructure))


@dataclass
class SubstrateContext(Context):
    """Access the substrate of the current design. Note that for normal use
    there's a :py:attr:`jitx.Current.subtrate` convenience property that can be
    used instead.

    >>> class MyDesign(Design):
    ...     substrate = MySubstrate()
    ...     circuit = MyCircuit()

    >>> class MyCircuit(Circuit):
    ...     def __init__(self):
    ...         assert isinstance(SubstrateContext.require().substrate, MySubstrate)
    ...         # or the preferred and equivalent
    ...         assert isinstance(jitx.current.substrate, MySubstrate)
    """

    substrate: Substrate
    """The substrate in the current design context."""


class FabricationConstraints(Critical):
    """Fabrication constraints for a substrate. These constraints are used to
    ensure that the design is manufacturable. Unless otherwise specified, these
    constraints are not enforced by the jitx engine. They are used for
    documentation purposes and can be queried by user code to generate
    appropriate design elements."""

    min_copper_width: float
    """Minimum permissible copper width. This constraint will be enforced by
    the engine for generated copper shapes and will take precedence over other
    constraints and rules, such as trace width."""
    min_copper_copper_space: float
    """Minimum permissible copper-to-copper spacing. This constraint will be
    enforced by the engine for generated copper shapes and will take precedence
    over other constraints and rules, such as clearance."""
    min_copper_hole_space: float
    """Minimum permissible copper-to-hole spacing. This constraint will be
    enforced by the engine for generated copper shapes and will take precedence
    over other constraints and rules, such as clearance."""
    min_copper_edge_space: float
    """Minimum permissible copper-to-board-edge spacing. This constraint will be
    enforced by the engine for generated copper shapes and will take precedence
    over other constraints and rules, such as clearance."""

    min_annular_ring: float
    """Minimum annular ring around a hole or via."""
    min_drill_diameter: float
    """Minimum diameter of a hole either in a pad or a via."""
    min_pitch_leaded: float
    """Minimum distance between pad centers for leaded packages."""
    min_pitch_bga: float
    """Minimum distance between pad centers for BGA packages."""

    max_board_width: float
    """Maximum width of a board."""
    max_board_height: float
    """Maximum height of a board."""

    min_silkscreen_width: float
    """Minimum width of silkscreen."""
    min_silk_solder_mask_space: float
    """Minimum distance between silkscreen and soldermask features."""
    min_silkscreen_text_height: float
    """Minimum height of silkscreen text."""
    solder_mask_registration: float
    """Minimum distance between soldermask and the edge of a copper pad."""
    min_soldermask_opening: float
    """Minimum size of a soldermask opening shape."""
    min_soldermask_bridge: float
    """Minimum distance between two soldermask features."""

    min_th_pad_expand_outer: float
    """Minimum through-hole pad expansion on outer layers."""
    min_hole_to_hole: float
    """Minimum distance between two holes, such as through-hole pads or vias."""
    min_pth_pin_solder_clearance: float
    """Minimum distance from the outer edge of a through-hole pad to the
    soldermask."""
