"""
Signal integrity constraints and modeling
=========================================

This module provides classes for defining signal integrity constraints,
routing structures, and pin models.
"""

from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, replace
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Self, cast, overload

from jitx._structural import Critical, Structural, Structurable
from jitx.circuit import CurrentCircuit
from jitx.context import Context
from jitx.feature import (
    Custom,
    Cutout,
    Feature,
    KeepOut,
    MultiLayerFeature,
    SurfaceFeature,
)
from jitx.inspect import extract
from jitx.layerindex import Layers, LayerSet, Side
from jitx.net import Net, DiffPair, Port, TopologyNet, Topology, _PORT, _match_port_type
from jitx.constraints import FenceVia, ViaFencePattern

from logging import getLogger

from jitx.shapes.primitive import Empty
from jitx.toleranced import Toleranced
from jitx.units import PlainQuantity, ohm
from jitx.via import Via


logger = getLogger(__name__)


class SignalConstraint[T: Port](Structural):
    """
    SignalConstraint is the primary way to apply signal integrity constraints
    in a design. They are meant to encapsulate a set of conditions that
    generate the constraints for a given signal or set of signals. While it is
    possible to apply constraints directly to a signal topology, it is
    recommended to define a reusable ``SignalConstraint`` from specifications
    instead.

    Various examples of SignalConstraint implementations can be found in
    :py:mod:`JITX Standard Library protocols <jitxlib.protocols>`.

    This is a base class, create a subclass and override :py:meth:`constrain`
    to implement your own signal constraint.
    """

    def __init__(self):
        self.constrains: list[BaseConstrain] = []

    def add(self, *constrain: BaseConstrain) -> None:
        self.constrains.extend(constrain)

    @abstractmethod
    def constrain(self, src: T, dst: T):
        """Called to apply implementation specific constraints. Note that all
        constraints should be added to the container by calling
        :py:meth:`~SignalConstraint.add` on self. It is valid to just set
        member attributes as well, as with everything in JITX, but be aware
        that your constraint may be used multiple times with different
        topologies, and thus be careful with overwriting values (e.g. some
        constraints may use a single :py:class:`DiffPairConstraint` to
        constrain all its diff pairs).
        """
        pass

    def __find_signal_end(self, p: T, q: T) -> T:
        # XXX finding the signal end is useless for pin assigned topologies -
        # does it even make sense to find it for any case if we need to handle
        # the pin-assigned case anyway?
        # XXX should check that we aren't actually already starting at a component port
        # which would perhaps mean we need to delay this until the end?
        # TODO traverse BridgingPinModels
        visited: set[TopologyNet] = set()
        if cc := CurrentCircuit.get():
            for tn in extract(cc.circuit, TopologyNet):
                if tn not in visited:
                    visited.add(tn)
                    # if both p and q are in the same sequence, it's connecting the two,
                    # so look for something else.
                    if p in tn.sequence and q not in tn.sequence:
                        # p in sequence means tn must be [T]
                        tn = cast(TopologyNet[T], tn)
                        if p == tn.sequence[0]:
                            p = tn.sequence[-1]
                        elif p == tn.sequence[-1]:
                            p = tn.sequence[0]
                        else:
                            logger.warning(
                                "Port is in the middle of a topology while looking for signal end."
                            )
            return p
        else:
            logger.warning("No active circuit while applying topology constraint")
            return p

    def constrain_topology(self, src: T, dst: T):
        """Construct topology and apply the constraint end-to-end.

        >>> class MyCircuit(Circuit):
        ...     a = ComponentCircuit()
        ...     b = ComponentCircuit()
        ...     cst = MyDiffPairConstraint()
        ...     def __init__(self):
        ...         with self.cst.constrain_topology(self.a.require(DiffPair), self.b.require(DiffPair)) as (src, dst):
        ...             # insert circuitry between src and dst here.
        ...             self += src >> dst
        """
        # ensure this runs even if the context manager is never entered.
        srcex = self.__find_signal_end(src, dst)
        dstex = self.__find_signal_end(dst, src)
        self.constrain(srcex, dstex)

        @contextmanager
        def constrain_topology():
            yield (src, dst)

        return constrain_topology()


class DiffPairConstraint(SignalConstraint[DiffPair]):
    """Basic signal constraint for a differential pair signal topology.
    Provides a simple declration of skew and insertion loss requirements for a
    diff pair signal. Often used inside a more complex protocol signal
    constraint."""

    def __init__(
        self,
        skew: Toleranced,
        loss: float,
        structure: DifferentialRoutingStructure | None = None,
    ):
        super().__init__()
        self.skew = skew
        self.loss = loss
        self.structure = structure

    def constrain(self, src: DiffPair, dst: DiffPair):
        super().constrain(src, dst)
        self.add(
            cdp := ConstrainDiffPair(Topology(src, dst))
            .timing_difference(self.skew)
            .insertion_loss(self.loss)
        )
        if self.structure:
            cdp.structure(self.structure)


class PinModel(Critical):
    """Simple model base class to describe signal propagation behavior as fixed delay and loss."""

    delay: Toleranced
    loss: Toleranced

    def __init__(self, delay: float | Toleranced, loss: float | Toleranced):
        if isinstance(delay, float | int):
            delay = Toleranced.exact(delay)
        if isinstance(loss, float | int):
            loss = Toleranced.exact(loss)
        self.delay = Toleranced.exact(delay)
        self.loss = Toleranced.exact(loss)


class BridgingPinModel[T: Port](PinModel, Structural):
    """A pin model the describes the signal propagation through a component
    from one port to another at the frequency of interest. Ideally this is
    included in the component definition, but can also be added to the circuit
    when used, if it doesn't already have one.

    Args:
        portA: The first port of the pin model.
        portB: The second port of the pin model.
        delay: The propagation delay through the component in seconds.
        loss: The insertion loss through the component in dB.

    >>> class MyComponent(Component):
    ...     a = Port()
    ...     b = Port()
    ...     pin_model = BridgingPinModel(a, b, delay=6e-12, loss=3)

    >>> class MyCircuit(Circuit):
    ...     r = Resistor()
    ...     def __init__(self):
    ...         self.aux_pin_model = BridgingPinModel(self.r.a, self.r.b, delay=6e-12, loss=3)
    """

    ports: tuple[T, T]

    @overload
    def __init__(
        self,
        portA: T,
        portB: T,
        /,
        *,
        delay: float | Toleranced,
        loss: float | Toleranced,
    ): ...

    @overload
    def __init__(
        self,
        ports: tuple[T, T],
        /,
        *,
        delay: float | Toleranced,
        loss: float | Toleranced,
    ): ...

    def __init__(
        self,
        portA: T | tuple[T, T],
        portB: T | None = None,
        /,
        *,
        delay: float | Toleranced,
        loss: float | Toleranced,
    ):
        super().__init__(delay=delay, loss=loss)
        if isinstance(portA, tuple):
            assert portB is None
            self.ports = portA
        else:
            assert portB is not None
            self.ports = portA, portB


class TerminatingPinModel[T: Port](PinModel, Structural):
    """A pin model the describes the signal propagation from a component port
    into the relevant part of the component at frequency of interest. Ideally
    this is included in the component definition, but can also be added to the
    circuit when used, if it doesn't already have one.

    Args:
        port: The port of the pin model.
        delay: The propagation delay into the component in seconds.
        loss: The insertion loss into the component in dB.

    >>> class MyComponent(Component):
    ...     a = Port()
    ...     pin_model = TerminatingPinModel(a, delay=6e-12, loss=3)

    >>> class MyCircuit(Circuit):
    ...     ic = MyComponent()
    ...     def __init__(self):
    ...         self.aux_pin_model = TerminatingPinModel(self.ic.a, delay=6e-12, loss=3)
    """

    port: T

    def __init__(self, port: T, *, delay: float, loss: float):
        super().__init__(delay=delay, loss=loss)
        self.port = port


@dataclass
class Constraint(Critical):
    """Base class for all signal integrity constraints."""

    pass


class BaseConstrain(Structural):
    """Base class for applying constraints to signal topologies."""

    _constraints: list[Constraint | RoutingStructureConstraint]
    """List of constraints applied to this topology."""

    def __init__(self):
        super().__init__()
        self._constraints = []

    def _individual(self) -> Iterable[Topology]:
        raise NotImplementedError(
            "Please use a concrete constraint strategy, e.g. Constrain"
        )

    @overload
    def insertion_loss(self, high: float, low: float = 0): ...
    @overload
    def insertion_loss(self, window: Toleranced, /): ...
    def insertion_loss(self, high: float | Toleranced, low: float = 0):
        """Apply an insertion loss constraint to the signal topology.

        Parameters:
            high: Maximum insertion loss allowed.
            low: Minimum insertion loss allowed. Default is 0.
        """
        if isinstance(high, Toleranced):
            low = high.min_value
            high = high.max_value
        self._constraints.append(InsertionLossConstraint(low, high))
        return self

    @overload
    def timing(self, high: float, low: float = 0): ...
    @overload
    def timing(self, window: Toleranced, /): ...
    def timing(self, high: Toleranced | float, low: float = 0):
        """Apply a timing constraint to the signal topology.

        Parameters:
            high: Maximum delay allowed.
            low: Minimum delay allowed. Default is 0.
        """
        if isinstance(high, Toleranced):
            low = high.min_value
            high = high.max_value
        self._constraints.append(TimingConstraint(low, high))
        return self


class Constrain(BaseConstrain):
    """Constrain a single signal topology. This is most commonly used inside a
    :py:class:`SignalConstraint` (which encapsulates more complex constraint
    configurations), and not to constrain a signal topology directly."""

    topologies: Sequence[Topology]
    """Signal topologies to constrain."""
    _structure: RoutingStructureConstraint | None = None
    """Optional routing structure constraint."""

    def __init__(self, topologies: Topology | Iterable[Topology]):
        super().__init__()
        self.topologies = (
            (topologies,) if isinstance(topologies, Topology) else tuple(topologies)
        )

    def _individual(self) -> Iterable[Topology]:
        return self.topologies

    def structure(
        self,
        structure: RoutingStructure,
        *,
        ref_layers: Mapping[int, RefLayerType] | None = None,
    ):
        """Apply a routing structure constraint to the signal topology.

        Parameters:
            structure: The routing structure to apply.
            ref_layers: A mapping of layers to reference plane nets.
        """
        self._structure = RoutingStructureConstraint(structure, ref_layers=ref_layers)
        return self


class BaseConstrainPairwise(BaseConstrain):
    """Constrain signal topologies pairwise. This is a base class that declares
    the :py:meth:`_pairwise` method."""

    _pairwise_constraints: list[Constraint | DifferentialRoutingStructureConstraint]

    def __init__(self):
        super().__init__()
        self._pairwise_constraints = []

    def _individual(self) -> Iterable[Topology]:
        # redefined to make a better error message
        raise NotImplementedError(
            "Please use a concrete difference constraint strategy, e.g. ConstrainReferenceDifference"
        )

    def _pairwise(self) -> Iterable[tuple[Topology, Topology]]:
        raise NotImplementedError(
            "Please use a concrete difference constraint strategy, e.g. ConstrainReferenceDifference"
        )

    @overload
    def timing_difference(self, high: float, low: float | None = None) -> Self: ...
    @overload
    def timing_difference(self, window: Toleranced, /) -> Self: ...
    def timing_difference(
        self, high: Toleranced | float, low: float | None = None
    ) -> Self:
        """Apply a timing difference constraint between two signal topologies.

        Parameters:
            high: Maximum timing difference allowed.
            low: Minimum timing difference allowed. If not provided, it is set to -high.
        """
        if isinstance(high, Toleranced):
            low = high.min_value
            high = high.max_value
        elif low is None:
            low = -high
        self._pairwise_constraints.append(TimingDifferenceConstraint(low, high))
        return self


class ConstrainReferenceDifference(BaseConstrainPairwise):
    """Constrain multiple signals to a single reference signal. Timing
    difference constraints will be applied to all signals, using the guide as
    reference. Timing and loss constraints apply to all, including the guide."""

    guide: Topology[Port]
    topologies: Sequence[Topology]

    def __init__(
        self, guide: Topology[Port], topologies: Topology | Iterable[Topology]
    ):
        super().__init__()
        self.guide = guide
        if not guide.begin.is_single_pin():
            # XXX should diff-pairs be explicitly allowed?
            raise ValueError("Guide must be a single pin type")
        self.topologies = (
            (topologies,) if isinstance(topologies, Topology) else tuple(topologies)
        )

    def _individual(self) -> Iterable[Topology]:
        yield self.guide
        yield from self.topologies

    def _pairwise(self) -> Iterable[tuple[Topology, Topology]]:
        guide = self.guide
        for topo in self.topologies:
            yield guide, topo


class ConstrainDiffPair(BaseConstrainPairwise):
    """Apply constraints within diff-pair signals. Timing difference
    constraints will effectively be skew constraints. Timing and loss apply to
    all P and N individually."""

    topologies: Sequence[Topology[DiffPair]]
    _structure: DifferentialRoutingStructureConstraint | None = None

    def __init__(self, topologies: Topology[DiffPair] | Iterable[Topology[DiffPair]]):
        super().__init__()
        self.topologies = (
            (topologies,) if isinstance(topologies, Topology) else tuple(topologies)
        )

    def _individual(self) -> Iterable[Topology]:
        for dp in self.topologies:
            yield Topology(dp.begin.p, dp.end.p)
            yield Topology(dp.begin.n, dp.end.n)

    def _pairwise(self) -> Iterable[tuple[Topology, Topology]]:
        for dp in self.topologies:
            yield Topology(dp.begin.p, dp.end.p), Topology(dp.begin.n, dp.end.n)

    def structure(
        self,
        structure: DifferentialRoutingStructure,
        *,
        ref_layers: Mapping[int, RefLayerType] | None = None,
    ):
        """Apply a differential routing structure constraint to the signal topology.

        Parameters:
            structure: The differential routing structure to apply.
            ref_layers: A mapping of layers to reference plane nets.
        """
        self._structure = DifferentialRoutingStructureConstraint(
            structure, ref_layers=ref_layers
        )
        return self


@dataclass
class TimingConstraint(Constraint):
    """
    A timing constraint that can be applied to a signal topology.
    The `min_delay` and `max_delay` are relative delays limits in units of seconds.
    """

    min_delay: float
    """Minimum delay in seconds."""
    max_delay: float
    """Maximum delay in seconds."""


@dataclass
class InsertionLossConstraint(Constraint):
    """
    An insertion loss constraint that can be applied to a signal topology.
    The `min_loss` and `max_loss` are relative attenuation limits in units of dB.
    """

    min_loss: float
    """Minimum insertion loss in decibels."""
    max_loss: float
    """Maximum insertion loss in decibels."""

    # TODO: Ensure max_loss > min_loss? (And likewise check for other constraints?)


@dataclass
class TimingDifferenceConstraint(Constraint):
    """
    A timing difference constraint that can be applied between two signal topologies.
    The `min_delta` and `max_delta` are relative skew limits in units of seconds between the two signal routes to be constrained.
    It is typical in most applications for `min-delta` to be negative and `max-delta` to be positive.
    """

    min_delta: float
    """Minimum timing difference in seconds."""
    max_delta: float
    """Maximum timing difference in seconds."""


class RoutingStructure:
    """Routing structure definition.

    A :py:func:`symmetric_routing_layers` function is available to create a
    symmetric routing structure by specifying just half of the layers, assuming
    that it's valid to use symmetric values.

    >>> class MySubstrate(Substrate):
    ...     RS_50 = RoutingStructure(
    ...         impedance=50,
    ...         layers={
    ...             0: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...             1: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...             -2: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...             -1: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...         }
    ...     )

    >>> class MySubstrate(Substrate):
    ...     RS_50 = RoutingStructure(
    ...         impedance=50,
    ...         layers=symmetric_routing_layers({
    ...             0: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...             1: RoutingStructure.Layer(trace_width=0.2, velocity=150e6, insertion_loss=0.01),
    ...         })
    ...     )
    """

    @dataclass(kw_only=True)
    class NeckDown:
        """Neck down parameters for routing layer."""

        trace_width: float | None = None
        clearance: float | None = None
        insertion_loss: float | None = None
        velocity: float | None = None

    @dataclass(kw_only=True)
    class Layer(Critical):
        """Routing layer definition."""

        trace_width: float
        """Width of traces on this layer."""
        velocity: float
        """Velocity of signal for purposes of timing constraints, in millimeters per second."""
        insertion_loss: float
        """Insertion loss of traces on this layer, in decibels per millimeter."""
        clearance: float | None = None
        """Minimum clearance to other objects on this layer, in millimeters."""
        neck_down: RoutingStructure.NeckDown | None = None
        """Routing parameters to apply in neckdown regions."""

        def __post_init__(self):
            self.__reference: list[_RefLayer] = []
            self.__geometry: list[_AddGeom] = []
            self.__fence: _StructureViaFence | None = None

        def _invert(self):
            ob = replace(self)
            ob.__reference = [rl._invert() for rl in self.__reference]
            ob.__geometry = [g._invert() for g in self.__geometry]
            if self.__fence:
                ob.__fence = self.__fence._invert()
            return ob

        @overload
        def geometry[T: SurfaceFeature](
            self, feature: type[T], width: float, *, side: Side
        ) -> Self: ...
        @overload
        def geometry[T: MultiLayerFeature](
            self, feature: type[T], width: float, *, layers: Layers
        ) -> Self: ...
        @overload
        def geometry(
            self, feature: type[KeepOut], width: float, *, layers: Layers, pour=False
        ) -> Self: ...
        @overload
        def geometry(
            self, feature: type[Custom], width: float, *, side: Side, name: str
        ) -> Self: ...
        @overload
        def geometry(self, feature: type[Cutout], width: float) -> Self: ...

        def geometry(self, feature: type[Feature], width: float, **kwargs) -> Self:
            """Add routing structure geometry for this routing layer. The
            generated feature will follow the shape if the created route, with
            the desired width, and can be on layers other than the current one.
            This is particularly useful if generating KeepOut voids in between
            this layer and a reference layer.

            .. note:: It's currently not supported to generate route KeepOuts.

            Args:
                feature: The feature type to add.
                desired_width: The desired width of the feature that will
                    follow the generated route.
            """
            if "layers" in kwargs:
                # allow construction of LayerSet from Layers. The only "layers"
                # argument in Feature is LayerSet; this is valid as long as
                # that's true. It would be cleaner to add this as input
                # preprocessing in MultiLayerFeature, but dataclasses don't
                # have good support for that.
                kwargs["layers"] = LayerSet(kwargs["layers"])
            self.__geometry.append(_AddGeom(feature(Empty(), **kwargs), width))
            return self

        # Can be done with a paramspec (without overloads), which will provide
        # correct type checking, but won't provide language server suggestions,
        # so let's go with overloads instead.
        # def geometry[**P](self, feature: Callable[Concatenate[Shape, P], Feature], desired_width: float, *args: P.args, **kwargs: P.kwargs) -> Self:
        #     self.__geometry.append(AddGeom(feature(Empty(), *args, **kwargs), desired_width))
        #     return self

        @overload
        def reference(self, layer: int, /, desired_width: float) -> Self: ...
        @overload
        def reference(self, layers: Mapping[int, float], /) -> Self: ...

        def reference(
            self, layer: int | Mapping[int, float], desired_width: float | None = None
        ) -> Self:
            """Specify that there should be a reference plane on the given
            layer, with the desired width surrounding the route. An attempt
            will be made to ensure there is a contiguous reference plane on
            that layer, but it is not guaranteed.

            Args:
                layer: The layer number of the reference plane.
                desired_width: The desired width of the reference plane
                    surrounding the route.
                layers: Alternatively, a mapping of layer numbers to desired
                    widths can be used to declare multiple reference planes at
                    once.
            """
            if isinstance(layer, Mapping):
                for layeridx, width in layer.items():
                    self.__reference.append(_RefLayer(layeridx, width))
            elif desired_width is not None:
                self.__reference.append(_RefLayer(layer, desired_width))
            else:
                raise TypeError("Must specify desired_width if layer is not a mapping")
            return self

        @overload
        def fence(
            self, fence: FenceVia, /, *, reference_layer: int | None = None
        ) -> Self: ...
        @overload
        def fence(
            self,
            via: type[Via],
            pattern: ViaFencePattern,
            *,
            reference_layer: int | None = None,
        ) -> Self: ...
        def fence(
            self,
            via: type[Via] | FenceVia,
            pattern: ViaFencePattern | None = None,
            *,
            reference_layer: int | None = None,
        ) -> Self:
            """Specify that there should be a via fence around the perimeter of
            the route. Unless otherwise specified, the vias will be given the
            same net as the first reference plane specified in the routing
            structure.

            Args:
                via: The Via class to use for fencing.
                pattern: The geometric pattern for fence placement.
                fence: Alternatively, a prepared FenceVia can be used to
                    specify the via and pattern in one go.
                reference_layer: An optional layer index to use as reference
                    for the via fence. The generated vias will be given the
                    same net as the reference plane on that layer. Note that
                    this does not imply that a this layer is a reference plane
                    for the signal. Note that the via fence will be generated
                    regardless whether there actually is a reference plane on this
                    layer. This can parameter can also be used, for example, to
                    generate a via fence using planes far away from the signal
                    (e.g. using through-hole vias), but are not actually
                    reference planes, should that ever be necessary.
            """
            if reference_layer is None:
                if not self.__reference:
                    raise ValueError(
                        "No reference plane specified in the routing"
                        " structure, and none provided, cannot specify a via"
                        " fence without a reference plane."
                    )
                reference_layer = self.__reference[0].layer
            if isinstance(via, FenceVia):
                pattern = via.pattern
                via = via.definition
            elif pattern is None:
                raise TypeError("Must specify pattern if no FenceVia specified")

            self.__fence = _StructureViaFence(via, pattern, reference_layer)
            return self

    layers: Mapping[int, Layer]
    impedance: PlainQuantity
    __name: str | None = None

    def __init__(
        self,
        layers: Mapping[int, Layer] | None = None,
        *,
        impedance: PlainQuantity | float,
        name: str | None = None,
    ):
        if layers is not None:
            self.layers = layers
        else:
            # assume these have been set by a subclass
            if not hasattr(self, "layers"):
                raise TypeError(
                    "RoutingStructure must be constructed with a mapping of layers, either directly or via a subclass field."
                )
        self.impedance = ohm.from_(impedance, strict=False, name="impedance")
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name or self.__class__.__name__

    def __repr__(self):
        if self.__name is None:
            return f"{self.__class__.__name__}(impedance={self.impedance:g~P})"
        else:
            return f"RoutingStructure(name={self.name}, impedance={self.impedance:g~P})"

    def __str__(self):
        return self.name


class DifferentialRoutingStructure:
    """Differential routing structure definition."""

    @dataclass(kw_only=True)
    class NeckDown(RoutingStructure.NeckDown):
        """Neck down parameters for differential routing layer."""

        pair_spacing: float | None = None

    @dataclass(kw_only=True)
    class Layer(RoutingStructure.Layer):
        """Differential routing layer definition."""

        pair_spacing: float
        """Internal spacing within the differential pair, in millimeters."""

    layers: Mapping[int, Layer]
    uncoupled_region: RoutingStructure | None = None
    impedance: PlainQuantity
    __name: str | None = None

    def __init__(
        self,
        layers: Mapping[int, Layer] | None = None,
        uncoupled_region: RoutingStructure | None = None,
        *,
        impedance: PlainQuantity | float,
        name: str | None = None,
    ):
        if layers is not None:
            self.layers = layers
        else:
            # assume these have been set by a subclass
            if not hasattr(self, "layers"):
                raise TypeError(
                    "DifferentialRoutingStructure must be constructed with a collection of layers,"
                    " either as constructor argument or using a subclass field."
                )
        if uncoupled_region is not None:
            self.uncoupled_region = uncoupled_region
        self.impedance = ohm.from_(impedance, strict=False, name="impedance")
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name or self.__class__.__name__

    def __repr__(self):
        return f"DifferentialRoutingStructure(name={self.name}, impedance={self.impedance:g~P})"

    def __str__(self):
        return self.name


@dataclass
class _StructureViaFence(FenceVia):
    """A via fence that is generated around a signal topology."""

    reference_layer: int | None = None
    """The layer index to use as reference for the via fence. The generated
    vias will be given the same net as the reference layer. Note that this does
    not imply that a this layer is a refernce plane for the signal. While
    likely the case, the via fence will be generated regardless of whether
    there is a reference plane on this layer. If not specified, the reference
    layer will be the first reference plane specified in the routing
    structure. If no such reference plane is speicified, an error will be
    generated."""

    _inverted: bool = False

    def _invert(self):
        start = self.definition.start_layer
        end = self.definition.stop_layer
        if start >= 0 != end >= 0:
            if -start - 1 != end:
                raise ValueError(
                    "Can only symmetrize via fences that use symmetric vias"
                )
        copy = replace(
            self,
            reference_layer=None
            if self.reference_layer is None
            else -self.reference_layer - 1,
        )
        copy._inverted = not self._inverted
        return copy


type RefLayerType = Net[Port]


def _reference_layers(
    ref_layers: Mapping[int, RefLayerType] | RefLayerType | None,
    structure: RoutingStructure | DifferentialRoutingStructure,
    container: Any,
) -> Mapping[int, RefLayerType]:
    # container is just for error reporting.
    all_nets: RefLayerType | None = None
    modifiable = {}
    if ref_layers:
        if isinstance(ref_layers, Mapping):
            for net in ref_layers.values():
                _match_port_type([net, _PORT], container)
            ref_layers = dict(ref_layers)
        else:
            _match_port_type([ref_layers, _PORT], container)
            all_nets = ref_layers
            ref_layers = modifiable
    else:
        planes = ReferencePlanes.get()
        if not planes:
            ref_layers = {}
        elif planes.all:
            all_nets = planes.all
            ref_layers = modifiable
        else:
            ref_layers = planes.layers
    for slayer in structure.layers.values():
        for rl in extract(slayer, _RefLayer):
            if all_nets:
                modifiable[rl.layer] = all_nets
            elif rl.layer not in ref_layers:
                raise ValueError(
                    f"Reference plane layers do not declare the required layer {rl.layer} from {structure}"
                )
        for svf in extract(slayer, _StructureViaFence):
            layer = svf.reference_layer
            if layer is None:
                raise ValueError("Unexpected missing reference layer for via fence")
            if all_nets:
                modifiable[layer] = all_nets
            elif layer not in ref_layers:
                raise ValueError(
                    f"Reference plane layers do not declare the required via fence reference layer {layer} from {structure}"
                )
    return ref_layers


class ReferencePlanes(Context, Structurable):
    """A context for specifying net assignments for reference layers used by
    routing structures. Nets of reference layers can also be specified directly
    when applying the routing structure, but this context allows a simple
    mechanism for declaring reference planes higher up in the design
    hierarchy.

    >>> class MyCircuit(Circuit):
    ...     GND = Net()
    ...     planes = ReferencePlanes({0: GND, 1: GND})
    ...     c = MyComponent()
    ...     def __init__(self):
    ...         self += self.c.p[0] >> self.c.p[1]

    Or if different reference planes are required for different parts of the
    design, the context can be activated separately. Note that this form can
    only be used inside the constructor function and will have no effect if
    used in the class variable context due to how JITX structural elements are
    instantiated.

    >>> class MyCircuit(Circuit):
    ...     GND1 = Net()
    ...     GND2 = Net()
    ...     c = MyComponent()
    ...     protocol = MyProtocolConstraint()
    ...     def __init__(self):
    ...         with ReferencePlanes(self.GND1):
    ...             with self.protocol.constrain_topology(selc.c.p[0].to(self.c.p[1])) as src, dst:
    ...                 self += src >> dst
    ...         with ReferencePlanes(self.GND2):
    ...             with self.protocol.constrain_topology(selc.c.p[0].to(self.c.p[1])) as src, dst:
    ...                 self += src >> dst


    Args:
        layers: A mapping of layer indices to nets. The nets will be assigned to
            the reference layers of the routing structure.
        all: Optionally a single net can be specified which will used for all
            reference layers.
    """

    all: RefLayerType | None = None
    layers: Mapping[int, RefLayerType]

    @overload
    def __init__(self, layers: Mapping[int, RefLayerType], /): ...
    @overload
    def __init__(self, all: RefLayerType, /): ...

    def __init__(self, layers: Mapping[int, RefLayerType] | RefLayerType, /):
        if isinstance(layers, Mapping):
            for net in layers.values():
                _match_port_type([net, _PORT], self)
            self.layers = dict(layers)
        else:
            _match_port_type([layers, _PORT], self)
            self.all = layers
            self.layers = {}


class RoutingStructureConstraint(Structurable):
    """A constraint to apply a routing structure to a signal topology."""

    structure: RoutingStructure
    ref_layers: Mapping[int, RefLayerType]

    def __init__(
        self,
        structure: RoutingStructure,
        *,
        ref_layers: Mapping[int, RefLayerType] | None = None,
    ):
        self.structure = structure
        self.ref_layers = _reference_layers(ref_layers, structure, self)


class DifferentialRoutingStructureConstraint(Structurable):
    """A constraint to apply a differential routing structure to a signal topology."""

    structure: DifferentialRoutingStructure
    ref_layers: Mapping[int, RefLayerType]

    def __init__(
        self,
        structure: DifferentialRoutingStructure,
        *,
        ref_layers: Mapping[int, RefLayerType] | None = None,
    ):
        self.structure = structure
        self.ref_layers = _reference_layers(ref_layers, structure, self)


def symmetric_routing_layers[T: RoutingStructure.Layer](
    layers: Mapping[int, T], invert_geometry=True
) -> dict[int, T]:
    """Create a symmetric routing structure from a dictionary of routing layers.

    Args:
        layers: Half of a routing structure layer set.
        invert_geometry: If True, the geometry of the inverted layers will be
            flipped appropriayle. If not, the geometry will be left as is. Note that
            via fences cannot currently be inverted unless they're using a via
            that's symmetric around the center of the board, since there's no
            practical way to specify a via for fencing on the other side of the
            board.
    """
    ret = dict(layers)
    for layer in layers:
        if invert_geometry:
            ret[-layer - 1] = layers[layer]._invert()
        else:
            ret[-layer - 1] = layers[layer]
    return ret


@dataclass
class _RefLayer(Critical):
    layer: int
    desired_width: float
    # required width is not yet supported
    # required_width: float | None = None

    def _invert(self):
        return replace(self, layer=-self.layer - 1)


@dataclass
class _AddGeom(Critical):
    feature: Feature
    width: float

    def _invert(self):
        return replace(self, feature=self.feature.invert())
