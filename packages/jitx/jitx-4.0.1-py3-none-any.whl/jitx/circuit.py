"""
Circuits
========

This module provides the Circuit class, which is the primary modularization
object in JITX for creating hierarchical designs with ports, components,
and subcircuits.
"""

from __future__ import annotations
from collections.abc import Mapping, Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Self, overload, override
from collections.abc import Callable
from weakref import ReferenceType, ref
import re

from jitx._structural import (
    Critical,
    InstanceField,
    Structurable,
    instantiation,
    Container,
)
from jitx.decorators import early, late
from jitx.context import Context
from jitx.symbol import Symbol

from .layerindex import Side
from .transform import IDENTITY, Point, Transform
from .placement import Placement, Positionable
from .net import Port, Provide

if TYPE_CHECKING:
    from jitx.component import Component


class Circuit(Positionable):
    """The Circuit is JITX's primary modularization object. The main function
    of a Circuit is instantiate ports that can be seen as an external
    interface, instantiate subcircuits or components, as well as net ports of
    these elements together.

    Ports, components, and other circuits can be created directly in the class
    for convenience, and will be instantiated separately as instance attributes
    for each created circuit instance. It's perfectly valid to add elements to
    ``self`` in the ``__init__`` method, and in fact, type of coding logic, such
    as a parameterized circuit, would need to go into an ``__init__`` method, as
    it's not possible to execute that properly in the class context.

    All elements of the circuit needs to be reachable from the circuit in some
    way, it is not sufficient to merely create a component, it must be assigned
    to member field in the circuit in some way. It can be added to a container
    (such as a list, or a dictionary) that is assigned to the circuit object,
    not every component needs have its own attribute. The same is true for nets.

    A general purpose ``+=`` operator is provided to add elements to the
    circuit that do not need an assigned name. They'll all be gathered into a
    private list that is not accessible from the outside. Note that if elements
    that have their name displayed somewhere (such as nets in the schematic)
    are added to this list, they will still be displayed, but their name may
    look confusing. For most objects it's advisable to either assign them to a
    field or add them to a list or mapping which are rendered in a sensible
    way.

    >>> class MyCircuit(Circuit):
    ...     # assume FancyComponent has an `n` and a `p` port. JITX's instantiation
    ...     # mechanism will create a new instance of FancyComponent for each
    ...     # instance of MyCircuit
    ...     comp = FancyComponent()
    ...     diffp = DiffPair()
    ...
    ...     def __init__(self):
    ...         self.nets = [
    ...             diffp.n + comp.n,
    ...             diffp.p + comp.p,
    ...         ]
    """

    in_bom: bool | None = None
    """Whether the components within this circuit are in the bill of materials. If unset, defers to the parent
    :py:class:`~jitx.circuit.Circuit`'s :py:attr:`~jitx.circuit.Circuit.in_bom`
    attribute. If there is no parent circuit, defaults to True."""
    soldered: bool | None = None
    """Whether the components within this circuit are soldered on the board. If unset, defers to the parent
    :py:class:`~jitx.circuit.Circuit`'s :py:attr:`~jitx.circuit.Circuit.soldered`
    attribute. If there is no parent circuit, defaults to True."""
    schematic_x_out: bool | None = None
    """Whether the components within this circuit are marked with a red X in the schematic. If unset, defers to the parent
    :py:class:`~jitx.circuit.Circuit`'s :py:attr:`~jitx.circuit.Circuit.schematic_x_out`
    attribute. If there is no parent circuit, defaults to False."""

    transform: Placement | None = Placement(IDENTITY)
    """The placement of this circuit relative to the parent circuit."""

    __iliad: list[Any] = InstanceField(list)

    @early
    def __push_context(self):
        instantiation.push()
        CurrentCircuit(self).set()

    @late
    def __pop_context(self):
        instantiation.pop()

    @overload
    def require[T: Port](
        self,
        Bundle: T | type[T],
        /,
        *,
        restrictions: Callable[[T], Mapping[Port, Callable[[Port], Any]]] | None = None,
    ) -> T: ...
    @overload
    def require[T: Port](
        self,
        Bundle: T | type[T],
        /,
        *,
        count: int,
        restrictions: Callable[[T], Mapping[Port, Callable[[Port], Any]]] | None = None,
    ) -> Sequence[T]: ...

    def require[T: Port](
        self,
        Bundle: T | type[T],
        /,
        *,
        count: int | None = None,
        restrictions: Callable[[T], Mapping[Port, Callable[[Port], Any]]] | None = None,
    ) -> T | Sequence[T]:
        """Require a port bundle to be provided a subcircuit, or,
        alternatively, by this circuit as a self-provide.

        Note that the returned port instance is a placeholder port for
        the provided port that can be netted with other ports, but
        should not be added to this circuit as a member field, as it's
        not a port that this circuit itself exposes.

        Args:
            Bundle: The port type or instance to require.
            restrictions: Optional function to specify restrictions on the
                required ports.
            count: Optional number of instances to require. If specified, a
                sequence of required ports are returned.

        Returns:
            The required port bundle instance.

        >>> class MyCircuit(Circuit):
        ...     subcircuit = MySubCircuit()
        ...     my_signal_port = DiffPair()
        ...     def __init__(self):
        ...         diffpair = self.subcircuit.require(DiffPair)
        ...         self.signal_net = self.my_signal__port + diffpair
        """
        if count is not None:
            return tuple(
                Provide.require(Bundle, self, restrictions) for _ in range(count)
            )
        return Provide.require(Bundle, self, restrictions)

    def __iadd__(self, other):
        self.__iliad.append(other)
        return self

    @overload
    def place[T: Component | Circuit](
        self,
        instance: T,
        placement: Placement,
        /,
        *,
        relative_to: Component | Circuit | None = None,
    ) -> T: ...
    @overload
    def place[T: Component | Circuit](
        self,
        instance: T,
        point: Point,
        /,
        *,
        on: Side = Side.Top,
        relative_to: Component | Circuit | None = None,
    ) -> T: ...
    @overload
    def place[T: Component | Circuit](
        self,
        instance: T,
        transform: Transform,
        /,
        *,
        on: Side = Side.Top,
        relative_to: Component | Circuit | None = None,
    ) -> T: ...

    def place[T: Component | Circuit](
        self,
        instance: T,
        placement: Placement | Transform | Point,
        /,
        *,
        on: Side = Side.Top,
        relative_to: Component | Circuit | None = None,
    ) -> T:
        """Place a component or circuit on the board relative to this circuit's
        frame of reference. It is different from :py:meth:`~jitx.circuit.Circuit.at`
        in that it does not modify the instance's actual placement in its
        parents frame of reference, but instead adds a placement request for a
        child circuit or component. If the instance is introspected before
        placement occurs, the placement will not be reflected in the instance's
        :py:class:`~jitx.inspect.Trace` transform.

        Note that circuits have a default placement of (0, 0) on top, which is
        to allow for elements inside the circuit to be placed relative to the
        design origin. If the circuit should have a free-floating frame of
        reference that components are placed relative to, the circuit should
        either be given a placement using :py:meth:`~jitx.circuit.Circuit.at`
        or explicitly set to be free floating using
        ``circuit.at(floating=True)``. Note that if the circuit is free
        floating and components inside the circuit are not placed, it is
        ambiguous which frame of reference is modified when the components are
        placed.

        >>> class MyCircuit(Circuit):
        ...     def __init__(self):
        ...         self.component = MyComponent()
        ...         self.place(self.component, Transform.rotate(90))
        """
        if isinstance(instance, Circuit):
            # if we're making a placement request for a subcircuit, we need to
            # ensure that the subcircuit does not have a local transform.
            instance.at(floating=True)
        self += InstancePlacement(instance, Placement(placement, on=on), relative_to)
        return instance

    def annotate(self, text: str, *, normalize=True) -> None:
        """Add a schematic annotation.

        Args:
            text: Markdown formatted text to add as an annotation.
            normalize: Whether to normalize the indentation, this is on by
                default, and is useful to allow natural indentation of
                multiline strings.

        >>> class MyCircuit(Circuit):
        ...     def __init__(self):
        ...         self.annotate("Hello, world!")
        """
        if normalize:
            text = text.rstrip()
            common = min(
                (len(match.group(1)) for match in re.finditer(r"\n( *)", text)),
                default=0,
            )
            if common:
                text = re.sub(r"\n {" + str(common) + "}", r"\n", text)
        self += Annotation(text)

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

    @overload
    def at(self, /, *, floating: Literal[True]) -> Self: ...

    @override
    def at(
        self,
        x: Placement | Transform | Point | float | None = None,
        y: float | None = None,
        /,
        *,
        on: Side = Side.Top,
        rotate: float = 0,
        floating: bool = False,
    ) -> Self:
        """Place the circuit on the board relative to its parent's frame of reference.

        Args:
            x: x-value, transform, or placement to adopt.
            y: y-value if x is an x-value. This argument is only valid in that context.
            on: If set to bottom, this object will be placed on the "opposite"
                side from its frame of reference. This means if the frame of
                reference is on the bottom of the board, setting this to "bottom"
                will actually put the object back on top.
            rotate: Rotation in degrees to apply to the object. Only applicable
                if not supplying a transform or placement.
            floating: If set to True, no other arguments are valid, and will
                allow this circuit to be free floating, subject to interactive
                placement.
        Returns:
            The circuit itself, for method chaining.
        """
        if floating:
            self.transform = None
            return self
        if y is not None:
            assert isinstance(x, float | int)
            return super().at(x, y, on=on, rotate=rotate)
        else:
            assert isinstance(x, Placement | Transform | tuple)
            return super().at(x, on=on)


@dataclass
class Annotation:
    """A text entity in the schematic. Typically not used directly,
    but rather through the convenience method
    :py:meth:`~Circuit.annotate` which also normalizes the
    indentation."""

    text: str


class SchematicGroup(Structurable):
    """A schematic group defines elements that will be placed together under a single
    logical grouping in the schematic. The group's name is derived from the name of
    the instance attribute used to define the SchematicGroup object.

    >>> class MyCircuit(Circuit):
    ...     comp = MyComponent()
    ...     def __init__(self):
    ...         # Add 'comp' to the schematic group named 'my_group'
    ...         self.my_group = SchematicGroup(self.comp)
    """

    @overload
    def __init__(self, /): ...
    @overload
    def __init__(self, elem: Circuit | Component | Symbol | Container, /): ...
    @overload
    def __init__(
        self, elems: Iterable[Circuit | Component | Symbol | Container], /
    ): ...
    @overload
    def __init__(
        self,
        elem: Circuit | Component | Symbol | Container,
        /,
        *elems: Circuit | Component | Symbol | Container,
    ): ...

    def __init__(
        self,
        elem: Circuit
        | Component
        | Symbol
        | Container
        | Iterable[Circuit | Component | Symbol | Container]
        | None = None,
        /,
        *elems: Circuit | Component | Symbol | Container,
    ):
        """Initialize a schematic group with elements to be grouped together.

        Args:
            elem: A single element or an iterable of elements to group.
            *elems: Additional elements to include in the group. Can be individual
                elements or iterables of elements.

        Valid elements are:
        - :py:class:`~jitx.circuit.Circuit`
        - :py:class:`~jitx.component.Component`
        - :py:class:`~jitx.symbol.Symbol`
        - :py:class:`~jitx.container.Container`
        - Iterable of the above

        If no arguments are provided, all elements will be grouped together
        under a single group, unless additional schematic groups are added.
        """
        # Handle empty initialization
        if elem is None:
            if elems:
                raise ValueError("SchematicGroup provided None and additional elements")
            self.elems = ()
        else:
            # Flatten the arguments: if elem is a sequence, use it; otherwise wrap it in a tuple
            if isinstance(elem, Iterable):
                elem_tuple = tuple(elem)
            else:
                elem_tuple = (elem,)

            # Flatten any iterables in *elems
            flattened_elems = []
            for e in elems:
                if isinstance(e, Iterable):
                    flattened_elems.extend(e)
                else:
                    flattened_elems.append(e)

            self.elems = elem_tuple + tuple(flattened_elems)


@dataclass
class CurrentCircuit(Context):
    """The current circuit being processed. Should not be used directly, but
    rather accessed through :py:attr:`jitx.current.circuit` instead.

    >>> def get_ports() -> list[Port]:
    ...    circuit = jitx.current.circuit
    ...    ports = extract(circuit, Port)
    ...    return list(ports)
    """

    circuit: Circuit


class InstancePlacement(Critical):
    """A placement of a component or circuit relative to another component or circuit.

    These are created by the :py:meth:`~jitx.circuit.Circuit.place` method, and
    do not need to be created manually.
    """

    instance: ReferenceType[Component | Circuit]
    """The component or circuit to place."""
    placement: Placement
    """The placement of the component or circuit."""
    relative_to: ReferenceType[Component | Circuit] | None = None
    """The circuit or component to place relative to. If not provided, the placement is relative to the circuit's frame of reference."""

    def __init__(
        self,
        instance: Component | Circuit,
        placement: Placement,
        relative_to: Component | Circuit | None = None,
    ):
        self.instance = ref(instance)
        self.placement = placement
        if relative_to:
            self.relative_to = ref(relative_to)
        else:
            self.relative_to = None
