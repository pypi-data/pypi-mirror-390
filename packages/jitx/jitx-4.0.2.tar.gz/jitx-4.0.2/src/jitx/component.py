"""
Component definitions
=====================

This modules provides the :py:class:`Component` class, which represents a physical component
in a design, contains meta information about the component itself, and links
ports to landpatterns and symbols.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from jitx.units import PlainQuantity

from jitx._structural import InstanceField, instantiation
from jitx.decorators import early, late
from jitx.context import Context
from .placement import Positionable


class Component(Positionable):
    """Components are a structural element in JITX representing a physical
    component. Components are instantiated in a
    :py:class:`~jitx.circuit.Circuit` and contain a landpattern and a
    symbol, as well as :py:class:`~jitx.net.Port` objects that are mapped to
    landpattern pads and symbol pins.

    Valid elements in a component are:
        - :py:class:`~jitx.net.Port`
        - :py:class:`~jitx.landpattern.Landpattern`
        - :py:class:`~jitx.symbol.Symbol`
        - :py:class:`~jitx.landpattern.PadMapping`
        - :py:class:`~jitx.symbol.SymbolMapping`

    Note that if multiple landpatterns are specified, they will be combined
    into a single composite landpattern. Multiple symbols are permissible, and
    will end up in the schematic as independent symbols units.

    If there are no pad mappings, a default mapping will be created that maps
    ports to pads in order. Similarly if there are no symbol mappings, a default
    mapping will be created that will attempt to map all ports to symbol pins
    in order. If a port should have no pad mapping, or multiple pads need to
    mapped to a single port, a pad mapping must be explicitly created.

    >>> class MyComponent(Component):
    ...     VIN = Power()
    ...     aux = Port()
    ...
    ...     landpattern = MyLandpattern()
    ...     symbol = BoxSymbol()
    ...     def __init__(self):
    ...         self.mappings = [
    ...             PadMapping({
    ...                 self.VIN.Vp: self.landpattern.p[1],
    ...                 self.VIN.Vn: self.landpattern.p[2],
    ...                 self.aux: self.landpattern.p[3],
    ...             }),
    ...             SymbolMapping({
    ...                 self.VIN.Vp: self.symbol.power,
    ...                 self.VIN.Vn: self.symbol.ground,
    ...                 self.aux: self.symbol.data,
    ...             }),
    ...         ]

    It is perfectly valid to have a component definition that constructs the
    component dynamically given parameters. For example you could have a
    component class that reads a CSV file to generate the component's
    properties.
    """

    value: str | PlainQuantity | None = None
    """Value label string for this component."""
    mpn: str | None = None
    """Manufacturer part number for this component."""
    manufacturer: str | None = None
    """Manufacturer for this component."""
    reference_designator: str | None = None
    """Reference designator for this component. Note that this field should
    probably be left blank until after the component has been instantiated, or
    it will be the same (and thus trigger an error) for every component of the
    same type."""
    reference_designator_prefix: str | None = None
    """Reference designator prefix for this component. This will be used to
    generate a unique reference designator for each component of the same
    type.

    .. note::
        This field is a required data point for matching components between
        builds. If this value changes (including changing from unset to set),
        it *will* be treated as a new component, even if nothing else changes.
    """
    in_bom: bool | None = None
    """Whether this component is in the bill of materials. If unset, defers to
    the parent :py:class:`~jitx.circuit.Circuit`'s
    :py:attr:`~jitx.circuit.Circuit.in_bom` attribute. If a component is not in
    the bill of materials, then it can be considered to be non-populated."""
    soldered: bool | None = None
    """Whether this component is soldered on the board. If unset, defers to the
    parent :py:class:`~jitx.circuit.Circuit`'s
    :py:attr:`~jitx.circuit.Circuit.soldered` attribute. If a component is not
    soldered on the board but in the bill of materials, then it can be
    considered to a component that is orderable such as a jumper, screw or
    other mechanical components but not attached via a standard soldering
    process."""
    schematic_x_out: bool | None = None
    """Whether this component is marked with a red X in the schematic. If
    unset, defers to the parent :py:class:`~jitx.circuit.Circuit`'s
    :py:attr:`~jitx.circuit.Circuit.schematic_x_out` attribute. Enabling the
    red X on the component in the schematic can indicate that component should
    be treated differently (e.g. not in the bill of materials or not soldered
    depending on the state of the other flags). ::note"""

    @early
    def __early(self):
        instantiation.push()
        CurrentComponent(self).set()

    @late
    def __late(self):
        instantiation.pop()

    __iliad: list[Any] = InstanceField(list)

    def __iadd__(self, other):
        self.__iliad.append(other)
        return self


class MechanicalComponent(Component):
    """This is a subclass of :py:class:`~jitx.component.Component` that is used
    to represent mechanical components that are not in the bill of materials
    and are not soldered on the board.
    """

    in_bom = False
    soldered = False


class NonSolderedComponent(Component):
    """This is a subclass of :py:class:`~jitx.component.Component` that is used
    to represent components that are present in the bill of materials but are
    not soldered on the board.
    """

    in_bom = True
    soldered = False


class NonPopulatedComponent(Component):
    """This is a subclass of :py:class:`~jitx.component.Component` that is used
    to represent circuit components that are not present in the bill of
    materials and are also not soldered on the board but the landpattern is
    present on the board.

    ..  note:: This component status is commonly referred to as do-not-populate
        (DNP) or not-populated (NP)."""

    in_bom = False
    soldered = False


@dataclass
class CurrentComponent(Context):
    """Context object representing the currently active component during
    processing. Should not be used directly, but rather accessed through
    :py:data:`jitx.current`'s :py:attr:`~jitx.Current.component` instead.

    >>> def get_component_ports() -> list[Port]:
    ...    component = jitx.current.component
    ...    ports = extract(component, Port)
    ...    return list(ports)
    """

    component: Component
