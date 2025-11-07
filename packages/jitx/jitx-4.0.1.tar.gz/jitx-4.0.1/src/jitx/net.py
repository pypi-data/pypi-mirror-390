"""
Net connectivity
================

This module provides fundamental net connectivity classes including
Port, Net, TopologyNet, and related functionality for net connections.
"""

from __future__ import annotations
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Self, TYPE_CHECKING, TypeVar, cast, overload
from jitx._structural import dispose

from jitx.copper import Copper
from jitx.memo import memoize
from jitx.via import Via

from ._structural import (
    Critical,
    PrePostInit,
    Proxy,
    Ref,
    Structural,
    instantiation,
    _instantiate,
)
from .inspect import extract

if TYPE_CHECKING:
    from jitx.symbol import Symbol
    from jitx.circuit import Circuit
    from jitx.component import Component


class PortException(Exception):
    pass


@dataclass
class _NoConnect(Critical, Ref):
    """Metadata object marking a port as no-connect. Necessary to allow
    discovery of no-connect port in nested structures. Should not be used
    directly, use the :py:meth:`~jitx.net.Port.no_connect` method instead which
    will also properly allow introspection of the port as no-connect."""

    port: Port


@memoize
class Port(Structural):
    """A Port is the fundamental connectivity element of JITX. It is used to
    represent everything from "pins" of a component, to the "virtual" pins of a
    circuit, to the abstract ports that make up a pin-assignment problem.

    Ports can only be netted to other ports of the same concrete type, thus a
    subclass of Port can only be netted to the same subclass of port. For
    parameterized ports, they also need to match the same parameters.  To create
    a multi-signal port, create a subclass of Port with a member field for each
    signal. These are sometimes also referred to as "bundle" ports.

    Instantiating Port directly represents a single electrical signal, and is
    the only type that is allowed as a leaf in a complex Port structure.

    Ports can be netted together using the `+` operator. This will create a
    :py:class:`~jitx.net.Net` object that represents the netted ports. If the
    ports should be part of a signal topology where the order of the ports
    matters, use the `>>` operator. This will create a
    :py:class:`~jitx.net.TopologyNet` object that represents the netted ports
    that will only allow the ports to be connected in this particular order
    while routing. Note that you must use a topology net even if there is only
    two ports in the net if you wish to apply a signal integrity constraint.

    >>> class MyDualSignal(Port):
    ...     a = Port()
    ...     b = Port()

    >>> class MyDualAndClockSignal(Port):
    ...     dual = MyDualSignal()
    ...     clock = Port()
    """

    __no_connect: bool = False

    def __add__(self, other: Self | Copper | Via | Net[Self]) -> Net[Self]:
        return Net([self, other])

    def __rshift__(self, other: Self | TopologyNet[Self]) -> TopologyNet[Self]:
        if isinstance(other, TopologyNet):
            dispose(other)
            return TopologyNet((self,) + other.sequence)
        elif isinstance(other, Port):
            return TopologyNet(self, other)
        return NotImplemented

    def __repr__(self):
        return self.__class__.__qualname__

    def is_single_pin(self):
        return Proxy.forkbase(self) is _PORT

    def no_connect(self):
        """Mark this port as no-connect.

        >>> class MyComponent(Component):
        ...     port = Port()
        ...     # ...
        ...
        >>> class MyCircuit(Circuit):
        ...     component = MyComponent()
        ...     def __init__(self):
        ...         self.component.port.no_connect()
        """
        from jitx.circuit import CurrentCircuit
        from jitx.component import CurrentComponent

        if cc := CurrentComponent.get():
            cc.component += _NoConnect(self)
        elif cc := CurrentCircuit.get():
            cc.circuit += _NoConnect(self)
        else:
            raise RuntimeError(
                "Cannot mark a port as no-connect outside of a component or circuit"
            )
        if isinstance(self, Proxy):
            # If the port is a proxy, we need to override the proxy to set the no_connect flag.
            with Proxy.override():
                self.__no_connect = True
        else:
            self.__no_connect = True
        return self

    def is_no_connect(self) -> bool:
        """Check if this port is marked as no-connect."""
        return self.__no_connect

    def to(self, other: Self) -> Topology[Self]:
        """Refer to a topology between these two ports. This does not construct
        the signal topology itself, but is used to create a topology object
        which is used as an argument to other functions operating on
        topologies. To construct a signal topology, use the ``>>`` operator to
        construct :py:class:`~jitx.net.TopologyNet` and bridge components using
        the :py:class:`~jitx.si.BridgingPinModel`, and terminate the topology
        using the :py:class:`~jitx.si.TerminatingPinModel`. The pin-models can
        be added after the fact in a circuit if needed, but ideally they're
        already present in the component definition. After that, a signal
        constraint can applied to the end-to-end topology.

        >>> class MyCircuit(Circuit):
        ...     a = TransmitterComponent()
        ...     b = ReceiverComponent()
        ...     def __init__(self):
        ...         self.passive = Resistor(...)
        ...         p1, p2 = decompose(self.passive, Port)
        ...         self.signal = [
        ...             # Note: pin models are best added in the component
        ...             # definition, but can be added in the circuit after the
        ...             # fact if needed, as done here.
        ...             TerminatingPinModel(self.a.transmit, delay=2e-12, loss=0.1),
        ...             self.a.transmit >> p1,
        ...             BridgingPinModel(p1, p2, delay=10e-12, loss=0.1),
        ...             p2 >> self.b.receive,
        ...             TerminatingPinModel(self.b.receive, delay=2e-12, loss=0.1),
        ...         ]
        ...         self.constraint = Constrain(self.a.transmit.to(self.b.receive)).timing(50e-12)
        """
        return Topology(self, other)


with instantiation.require():
    _PORT = Proxy.forkbase(Port())  # the canonical Port object.


def port_array[T: Port](cnt: int, /, ptype: Callable[[], T] = Port) -> list[T]:
    """Convenience function to construct a list of ``Port()`` instances

    .. note::
        This function simply constructs a list of ``Port()`` instances, it does
        not create a bundle that can be used for netting. More importantly, if
        we attempt to construct a net using the result of this function, indeed
        it will most likely silently add the list of ports together, and not
        create a net for each element.

    Args:
        cnt: Number of ports in the constructed sequence
        ptype: Type or constructor of port for the constructed sequence. By
            default this functions uses :py:class:`Port`

    Returns:
        Sequence of port elements that make up a port array.
    """
    return [ptype() for _ in range(cnt)]


class PortArray[T: Port](Port):
    """A port array is a primitive array of single-signal ports. It's mainly
    intended as an example, and explicit bundles should be implemented
    instead.

    .. note::
        While this constructs a bundle that can be netted, it's currenetly not
        possible to use it as a sequence of individual ports where a
        :py:class:`Sequence` of ports is expected.
    """

    array: tuple[T, ...]

    @overload
    def __init__(self, array: Sequence[T], /) -> None: ...
    @overload
    def __init__(self, port: T, /, count: int) -> None: ...
    @overload
    def __init__(self: PortArray[Port], size: int, /) -> None: ...

    def __init__(
        self, array: Sequence[T] | type[T] | T | int, /, count: int | None = None
    ):
        if isinstance(array, type) and issubclass(array, Port) and count is not None:
            self.array = tuple(array() for _ in range(count))
        elif isinstance(array, Port) and count is not None:
            self.array = tuple(Proxy.create(array) for _ in range(count))
        elif isinstance(array, Sequence):
            self.array = tuple(array)
        elif isinstance(array, int):
            self.array = cast(tuple[T, ...], tuple(Port() for _ in range(array)))
        else:
            raise ValueError(
                "Improper PortArray instantiation, expected either port type and count or sequence of ports"
            )

    def __getitem__(self, index: int):
        return self.array[index]

    def __len__(self):
        return len(self.array)


def _match_port_type(
    s: Sequence[Port | Net | TopologyNet | Copper | Via], container
) -> Port | None:
    match = None
    for np in s:
        if isinstance(np, Net):
            if isinstance(container, TopologyNet):
                raise ValueError("Cannot add Net to TopologyNet")
            t = _match_port_type(np.connected, container)
        elif isinstance(np, TopologyNet):
            if isinstance(container, Net):
                raise ValueError("Cannot add TopologyNet to Net")
            t = _match_port_type(np.sequence, container)
        elif isinstance(np, Copper | Via):
            t = _PORT
        else:
            t = Proxy.forkbase(np)
        if t:
            if match and t is not match:
                raise ValueError(
                    f"Incompatible ports on {container.__class__.__name__}: {match.__class__.__name__} and {t.__class__.__name__}"
                )
            else:
                match = t
    return match


CoPort = TypeVar("CoPort", bound=Port, covariant=True)


def _check_options(
    opts: Iterable[Mapping[CoPort, CoPort] | Sequence[tuple[CoPort, CoPort]]],
) -> tuple[tuple[tuple[CoPort, CoPort], ...], ...]:
    unpacked = (opt.items() if isinstance(opt, Mapping) else opt for opt in opts)

    def antialias(o: CoPort) -> CoPort:
        while Proxy.is_ref(o):
            o = cast(CoPort, Proxy.of(o))
        return o

    out = tuple(tuple((a, antialias(b)) for (a, b) in mapping) for mapping in unpacked)
    for o in out:
        for a, b in o:
            if Proxy.forkbase(a) is not Proxy.forkbase(b):
                raise ValueError(
                    f"Unable to provide {a} with incompatible port type {b}"
                )
    return out


type _Restrictions = Mapping[Port, Callable[[Port], Any]]


class provide[T: Port]:
    """Decorator to help set up the pin-assignment problem. In the base form,
    the decorator is applied to a method of a circuit that will be given a
    bundle to map, and should return a list of possibilities how to map that
    bundle. Each returned options will be offered to requirements, so if 3
    options are returned, three different instances of this bundle can be
    required, served by each option. This is commonly known as the "pin
    swapping" case, where all options can be used, but it's not settled which
    is used where.

    For other provisioning schemes, see the :py:deco:`provide.one_of` and
    :py:deco:`provide.subset_of` decorators.

    Args:
        Bundle: The type of the bundle to provide

    >>> class MyBundle(Port):
    ...     a = Port()
    ...     b = Port()

    >>> class MyCircuit(Circuit):
    ...     # these are created here for demonstration purposes, we could just
    ...     # as easily refer to a component's ports.
    ...     internal_1 = Port(), Port()
    ...     internal_2 = Port(), Port()
    ...     @provide(MyBundle)
    ...     def provide_my_internals(self, bundle: MyBundle):
    ...         return [{
    ...             # first option
    ...             bundle.a: self.internal_1[0],
    ...             bundle.b: self.internal_1[1],
    ...         }, {
    ...             # second option
    ...             bundle.a: self.internal_2[0],
    ...             bundle.b: self.internal_2[1],
    ...         }]

    >>> class MyOtherCircuit(Circuit):
    ...     subcircuit = MyCircuit()
    ...     interfaces = MyBundle(), MyBundle()
    ...     def __init__(self):
    ...         self.nets = [
    ...             interfaces[0] + subcircuit.require(MyBundle),
    ...             interfaces[1] + subcircuit.require(MyBundle),
    ...         ]
    """

    type Provider = Callable[
        [Any, T], Iterable[Mapping[Port, Port]] | Iterable[Sequence[tuple[Port, Port]]]
    ]
    __wrapping: Callable[[Provider], PrePostInit]
    __bundle_type: T | type[T]

    def __init__(self, Bundle: T | type[T]):
        self.__bundle_type = Bundle
        self.__wrapping = self.__all_of

    def __bundle(self, deferred) -> T:
        if isinstance(self.__bundle_type, type):
            bundle = self.__bundle_type()
            assert bundle is not Port, "Can only provide bundle port types"
            return bundle
        else:
            bundle = _instantiate(self.__bundle_type, deferred)
            assert isinstance(bundle, Port), "Can only provide bundle port types"
            assert not Port.is_single_pin(bundle), (
                "Can only provide bundle port types, even for a single port, e.g. GPIO"
            )
            return cast(T, bundle)

    @classmethod
    def all_of(cls, Bundle: T | type[T]):
        """This is the default behavior and indeed an alias of using
        :py:class:`provide` directly without specifying a provisioning scheme.
        Each returned option will be offered to requirements, so if 3 options
        are returned, three different instances of this bundle can be required,
        served by each option. This is commonly known as the "pin swapping"
        case, where all options can be used, but it's not settled which is used
        where.

        Args:
            Bundle: The type of the bundle to provide
        """
        return cls(Bundle)

    def __all_of(self, method: Provider):
        provide = self

        def before(self, deferred):
            return [Provide(provide.__bundle(deferred))]

        def after(self, before: list[Provide[T]]):
            ps = before
            p0 = before[0]
            opts = tuple(method(self, p0.bundle))
            if not opts:
                return before
            for i in range(len(opts)):
                # this reuses the prebuilt p0, to avoid generating a warning in the finalizer
                if i:
                    p = Provide(p0.bundle)
                    ps.append(p)
                else:
                    p = p0
                p.options = _check_options([opts[i]])
            return ps

        return PrePostInit(before, after)

    def __call__(self, method: Provider):
        # cast for type checking- it will be a provide at runtime
        return cast(list[Provide[T]], self.__wrapping(method))

    @classmethod
    def one_of(cls, Bundle: T | type[T]):
        """Provide a single instance of the given bundle type, chosen from a
        list of possible options. The options may overlap with other provided
        functions. This is the dynamic function use case, where a function can
        served by multiple different ports, but there's only one instance of
        the function provided, e.g. a microcontroller has only one clock, but
        which pin it's on is not settled.

        Args:
            Bundle: The type of the bundle to provide
        """
        provide = cls(Bundle)
        provide.__wrapping = provide.__one_of
        return provide

    def __one_of(self, method: Provider):
        provide = self

        def before(self, deferred):
            return Provide(provide.__bundle(deferred))

        def after(self, before: Provide[T]):
            p = before
            p.options = _check_options(method(self, p.bundle))
            return p

        return PrePostInit(before, after)

    @classmethod
    def subset_of(cls, Bundle: T | type[T], n: int):
        """Similar to :py:deco:`provide.one_of`, but allows for ``n`` instances
        out of a list of options to be provided. This is equivalent to manually
        copying a :py:deco:`provide.one_of` decorated method ``n`` times.

        Args:
            Bundle: The type of the bundle to provide
            n: The number of instances to provide
        """
        provide = cls(Bundle)

        def wrapping(method: provide.Provider):
            def before(self, deferred):
                count = _instantiate(n, deferred)
                if not isinstance(count, int):
                    raise ValueError(
                        f"Expected integer for number of instances to provide, got {count}"
                    )
                bundle = provide.__bundle(deferred)
                if not isinstance(bundle, Port):
                    raise ValueError(f"Expected port for bundle type, got {bundle}")
                return [Provide(bundle) for _ in range(count)]

            def after(self, before: list[Provide[T]]):
                ps = before
                p0 = before[0]
                p0.options = _check_options(method(self, p0.bundle))
                for i in range(1, len(ps)):
                    p = ps[i]
                    p.options = p0.options
                return ps

            return PrePostInit(before, after)

        provide.__wrapping = wrapping
        return provide


class Provide[T: Port](Structural, Ref):
    """This is the general structure for setting up a pin-assignment problem.
    It is recommended to use one of the convenience decorators in
    :py:class:`~provide` instead, but if the full power of the pin-assignment
    system is needed in a way that is not covered by the decorators, or if you
    need programmatic control over the pin-assignment problem, then directly
    instantiating this class the appropriate number of times and populating the
    options in each may be a way to achieve that.

    The equivalent of the conenvience decorators are also available as
    methods on this class for use inside functions, such as ``__init__``.

    >>> class MyCircuit(Circuit):
    ...     def __init__(self, ports: int):
    ...         self.ports = [Port() for _ in range(ports)]
    ...         self.gpios = Provide(GPIO).all_of(lambda b: [{b.port: port} for port in self.ports])

    .. note ::
        Be aware of pythons binding of loop-variables, if you create Provides
        in a loop, you should bind the loop variable if it's used in the
        mapping function. Consider the functional equivalent of `.all_of` but
        using `.one_of` in the example below:

        >>> class MyCircuit(Circuit):
        ...     def __init__(self, ports: int):
        ...         self.ports = [Port() for _ in range(ports)]
        ...         self.gpios = [Provide(GPIO).one_of(lambda b, port=port: [{b.port: port}]) for port in ports]

        Note that the `port` argument is bound to the lambda function's body
        using a parameter with a default argument, instead of using the loop
        variable directly, which could potentially be bound to a different
        value by the time the lambda is called. In the current implementation,
        the lambda is called immediately, so the result would still be correct
        here, but it's a good practice to avoid this pitfall.

    Args:
        Bundle: The type of the bundle to provide
        mapping: The mapping function to use to populate the options
            for this Provide port. Note that this is the equivalent argument of calling
            :py:meth:`~Provide.one_of`, and it's recommended to use that method
            instead for clarity.
    """

    options: Sequence[Sequence[tuple[Port, Port]]]
    bundle: T

    type Provider = Callable[
        [T], Iterable[Mapping[Port, Port]] | Iterable[Sequence[tuple[Port, Port]]]
    ]

    def __init__(self, Bundle: T | type[T], mapping: Provider | None = None):
        self.options = ()
        self.bundle = Bundle() if isinstance(Bundle, type) else Bundle
        if mapping:
            self.one_of(mapping)

    def all_of(self, mapping: Provider) -> Sequence[Provide]:
        """Equivalent of the :py:deco:`provide.all_of` decorator, but can be
        constructed inside a function, such as ``__init__``. Useful when
        needing more parametric control over the pin-assignment problem. Note
        that this function will return a collection of ``Provide`` objects."""
        opts = _check_options(mapping(self.bundle))

        def pop(opt):
            p = Provide(self.bundle)
            p.options = _check_options([opt])
            return p

        if self.options:
            raise ValueError(
                "Cannot populate a Provide object that has already been populated"
            )
        Structural._dispose(self)
        return [pop(opt) for opt in opts]

    def one_of(self, mapping: Provider) -> Provide:
        """Equivalent of the :py:deco:`provide.one_of` decorator, but can be
        constructed inside a function, such as ``__init__``. Useful when
        needing more parametric control over the pin-assignment problem."""
        if self.options:
            raise ValueError(
                "Cannot populate a Provide object that has already been populated"
            )
        self.options = tuple(self.options) + _check_options(mapping(self.bundle))
        return self

    def subset_of(self, count: int, mapping: Provider) -> Sequence[Provide]:
        """Equivalent of the :py:deco:`provide.subset_of` decorator, but can be
        constructed inside a function, such as ``__init__``. Useful when
        needing more parametric control over the pin-assignment problem. Note
        that this function will return a collection of ``Provide`` objects."""
        if self.options:
            raise ValueError(
                "Cannot populate a Provide object that has already been populated"
            )
        if count < 1:
            raise ValueError(f"Need to provide at least one, got: {count}")
        opts = _check_options(mapping(self.bundle))

        def pop():
            p = Provide(self.bundle)
            p.options = opts
            return p

        Structural._dispose(self)
        return [pop() for _ in range(count)]

    @classmethod
    def require(
        cls,
        Bundle: T | type[T],
        provider: Circuit | Component,
        restrictions: Callable[[T], _Restrictions] | None = None,
    ) -> T:
        """This is the underlying framework function for requiring a bundle
        provided by a different circuit. Please use
        :py:class:`~jitx.circuit.Circuit`'s convenience
        :py:meth:`~jitx.circuit.Circuit.require` method instead.

        Args:
            Bundle: The bundle type to require
            provider: The provider instance
            restrictions: Optional function mapping single ports within a bundle to a restriction function
        """
        port = Bundle() if isinstance(Bundle, type) else Proxy.create(Bundle)
        # bypass frozen flag
        for subport in extract(port, Port):
            object.__setattr__(subport, "_Structurable__required_through", port)
        object.__setattr__(port, "_Structurable__provided_by", provider)

        # Store restrictions on the bundle
        if restrictions:
            object.__setattr__(port, "_Structurable__restrictions", restrictions(port))

        return port

    @classmethod
    def provided_by(cls, port: Port) -> None | Circuit | Component:
        return getattr(port, "_Structurable__provided_by", None)

    @classmethod
    def required_through(cls, port: Port) -> None | Port:
        return getattr(port, "_Structurable__required_through", None)

    @classmethod
    def restrictions_for(cls, port: Port) -> _Restrictions | None:
        """Get restrictions associated with a required bundle port."""
        return getattr(port, "_Structurable__restrictions", None)


class Net[T: Port](Structural):
    """
    Construct a net by connecting ports or other nets. Note that nets are
    constructed implicitly by adding ports and other nets together, and
    constructing a net explicitly only has the main benefit of declaring the
    net up front, and give it a name and/or symbol.

    Args:
        ports: Optional list of ports to initially add to the net
        name: Optional name of this net. If there are multiple named nets
            connected together, a net naming heuristic will pick one of them.
        symbol: Optional net symbol for this net. Only applicable to simple,
            non-bundle, nets.

    >>> Net(name="P5V5")
    Net(name="P5V5")

    >>> a, b = Port(), Port()
    >>> isinstance(a + b, Net)
    True
    """

    name: str | None = None
    connected: list[T | Net[T] | Copper | Via]
    _symbol: Symbol | None = None
    _port: T

    def __init__(
        self,
        ports: Iterable[T | Net[T] | Copper | Via] = (),
        *,
        name: str | None = None,
        symbol: Symbol | None = None,
    ):
        self.name = name
        self.connected = list(ports)
        self.symbol = symbol
        port = _match_port_type(self.connected, self)
        if not port:
            port = Port()
        # SubNets pretend to be ports.
        self._port = cast(T, SubNet(Proxy.create(port, ref=True), self))

    def __repr__(self):
        opts = []
        if self.name is not None:
            opts.append(f'name="{self.name}"')
        if self.symbol is not None:
            opts.append(f'symbol="{self.symbol}"')
        return f"Net({', '.join(opts)})"

    @property
    def port(self) -> T:
        return self._port

    @property
    def symbol(self) -> Symbol | None:
        return self._symbol

    @symbol.setter
    def symbol(self, value: Symbol | None) -> None:
        if value is not None:
            port_type = _match_port_type(self.connected, self)
            if port_type is not None and port_type is not _PORT:
                raise ValueError(
                    f"Cannot set symbol on bundle net: {port_type.__class__.__name__}"
                )
            self._symbol = value
        else:
            self._symbol = None

    @overload
    def __add__(self: Net[Port], other: Copper | Via) -> Net[Port]: ...
    @overload
    def __add__(self, other: T | Net[T]) -> Net[T]: ...
    def __add__(self, other: T | Net[T] | Copper | Via):
        net = Net([self, other])
        if isinstance(other, Copper | Via):
            # for Copper and Via overloads
            return cast(Net[Port], net)
        return net

    @overload
    def __iadd__(
        self: Net[Port], other: Port | Net[Port] | Copper | Via
    ) -> Net[Port]: ...
    @overload
    def __iadd__(self: Net[T], other: T | Net[T]) -> Net[T]: ...
    def __iadd__(self, other: T | Net[T] | Port | Net[Port] | Copper | Via):  # type: ignore
        # need the type ignore as the type narrowing is really tricky here to
        # get the overloads to match; runtime checks should ensure correctness.
        # NOTE if adding more overloads, triple check that the types are
        # accurate.
        if self.connected:
            _match_port_type([self, other], self)
        self.connected.append(other)  # type: ignore - checked at runtime, above
        return self

    def __contains__(self, other: T | Net[T] | Copper | Via):
        for c in self.connected:
            if other is c:
                return True
            elif isinstance(c, Net):
                return other in c

    @classmethod
    def zip(
        cls,
        first: Sequence[T | Net[T]],
        second: Sequence[T | Net[T]],
        *more: Sequence[T | Net[T]],
    ) -> Sequence[Net[T]]:
        """Zip multiple sequences of ports into a sequence of nets, where each
        net contains the corresponding ports from each sequence. For example,
        the first net in the returned sequence will contain the first port from
        each input sequence, the second net will contain the second port, and
        so on. This is particularly useful when dealing with arrays of ports
        that need to be connected in parallel.

        >>> a, b, c = Port(), Port(), Port()
        >>> x, y, z = Port(), Port(), Port()
        >>> u, v, w = Port(), Port(), Port()
        >>> n1, n2, n3 = Net.zip([a, b, c], [x, y, z], [u, v, w])
        >>> n1.connected == [a, x, u]
        True
        """
        return [Net(args) for args in zip(first, second, *more, strict=True)]


class SubNet[T: Port](Net[T], Ref):
    def __init__(self, port: T, base: Net):
        self._base = base
        self._subnetport = port
        self._port = cast(T, self)

    def __getattr__(self, attr):
        # in case we do things like property lookup on the subnet, then don't
        # recurse endlessly here.
        if attr.startswith("_"):
            raise AttributeError(attr)
        setattr(self, attr, sn := SubNet(getattr(self._subnetport, attr), self._base))
        return sn


class TopologyNet[T: Port](Structural):
    name: str | None = None
    sequence: tuple[T, ...]

    def __init__(self, sequence: T | Sequence[T], *args: T, name: str | None = None):
        self.name = name
        if isinstance(sequence, Sequence):
            # Sequence of ports
            self.sequence = tuple(sequence) + args
        else:
            # Multiple ports as separate arguments
            self.sequence = (sequence,) + args
        _match_port_type(self.sequence, self)

    def __rshift__(self, other: T | TopologyNet[T]) -> TopologyNet[T]:
        if isinstance(other, TopologyNet):
            dispose(self)
            dispose(other)
            return TopologyNet(self.sequence + other.sequence)
        elif isinstance(other, Port):
            dispose(self)
            return TopologyNet(self.sequence + (other,))
        return NotImplemented

    def __irshift__(self, other: T | TopologyNet[T]):
        if isinstance(other, TopologyNet):
            dispose(other)
            self.sequence += other.sequence
        else:
            self.sequence += (other,)
        return self


class Topology[T: Port]:
    """A topology is a description of a connectivity path, identified by it's
    start and end ports. This object does not construct the topology itself, it
    merely identifies the path and is used as an argument to other functions
    such as signal integrity constraints. To construct a topology, use the
    ``>>`` operator to construct :py:class:`TopologyNet` objects as well as
    declaring :py:class:`TerminatingPinModel` and :py:class:`BridgingPingModel`
    to construct the actual signal path, from end to end, potentially across
    components.
    """

    begin: T
    end: T

    def __init__(self, begin: T, end: T):
        assert begin is not end
        self.begin = begin
        self.end = end


class DiffPair(Port):
    """
    Bundles two pins `p` and `n`.
    The DiffPair base class bears special meaning and standardizes naming,
    any diff-pair type signal should inherit this base class.

    >>> class Transmission(DiffPair):
    ...     pass

    >>> class MDI:
    ...     tx = Transmission()
    ...     rx = Transmission()
    """

    p = Port()
    n = Port()


class ShortTrace(Net[Port]):
    """Indicates that the distance between two ports should be minimized. A
    ShortTrace is a type of net, and can be used as such.

    >>> class MyCircuit(Circuit):
    ...     a = MyComponent()
    ...     inp = Port()
    ...     out = Port()
    ...     def __init__(self):
    ...         self.nets = [
    ...             ShortTrace(a.p1, inp),
    ...             a.p2 + outp
    ...         ]
    """

    def __init__(self, p1: Port, p2: Port):
        super().__init__([p1, p2])
        # Ensure single ports
        _match_port_type([self, Port()], self)


class PortAttachment(Structural, Ref):
    """Indicates that a port should be connected to a copper or via.

    >>> class MyCircuit(Circuit):
    ...     c = MyComponent()
    ...     attachments = [
    ...         PortAttachment(c.p[0], Copper(0, Circle(diameter=1.0)).at(-5, 0)),
    ...         PortAttachment(c.p[1], SampleSubstrate.MicroVia().at(5, 0)),
    ...     ]
    """

    port: Port
    attachment: Copper | Via

    def __init__(self, port: Port, attachment: Copper | Via):
        self.port = port
        self.attachment = attachment
