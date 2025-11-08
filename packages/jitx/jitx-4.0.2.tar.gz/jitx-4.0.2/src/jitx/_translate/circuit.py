from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import cast

from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.pin_assignment_pb2 as ppb2
import jitxcore._proto.module_pb2 as mpb2

from .._structural import Container, Proxy, RefPath, pathstring, relativeref
from ..circuit import Annotation, Circuit, InstancePlacement, SchematicGroup
from ..component import Component
from ..feature import Feature
from ..inspect import decompose, extract, visit
from ..net import (
    Copper,
    Net,
    Port,
    PortAttachment,
    Provide,
    ShortTrace,
    SubNet,
    TopologyNet,
    _NoConnect,
    _Restrictions as Restrictions,
    _match_port_type,
    _PORT,
)
from ..constraints import BuiltinTag, Tag, Tags
from ..placement import Placement
from ..si import (
    BaseConstrain,
    BaseConstrainPairwise,
    BridgingPinModel,
    Constrain,
    ConstrainDiffPair,
    InsertionLossConstraint,
    SignalConstraint,
    TerminatingPinModel,
    TimingConstraint,
    TimingDifferenceConstraint,
)
from ..symbol import Pin, Symbol
from ..via import Via
from .. import UserCodeException
from .bundle import translate_bundle, translate_port_type
from .component import translate_component
from .copper import translate_copper
from .dispatch import Trace, dispatch
from .enums import translate_side
from .feature import translate_feature
from .fileinfo import translate_file_info
from .idmap import idmap, mapped
from .mapping import translate_port_mapping
from .routing import (
    translate_differential_routing_structure_constraint,
    translate_routing_structure_constraint,
)
from .rules import translate_user_tag
from .shape import translate_pose
from .symbol import translate_symbol
from .via import translate_via
from jitx._translate.signal_models import translate_pin_model


# Cache for restriction results to avoid redundant processing
_restriction_cache: dict[tuple[int, str, int, int], int] = {}


@dataclass
class InstanceStatus:
    in_bom: bool
    soldered: bool
    schematic_x_out: bool


@dataclass
class RestrictInfo:
    circuit: Circuit
    restricts: RepeatedCompositeFieldContainer[ppb2.RestrictEntry]


def flatten_net[T: Port](
    net: Net[T] | TopologyNet[T],
    ports: list[Port | Copper | Via],
    nets: list[Net[T] | TopologyNet[T]],
    shorts: list[ShortTrace],
    tags: set[Tag],
) -> tuple[
    str | None,  # name
    Symbol | None,  # symbol
]:
    name: str | None = None
    symbol: Symbol | None = None

    if idmap.visited(id(net)):
        # If the net has already been translated, add it as a subnet.
        nets.append(net)
    else:
        idmap(id(net))

        if isinstance(net, ShortTrace):
            shorts.append(net)
        if isinstance(net, Net):
            net = cast(Net[T], net)
            name = net.name
            symbol = net.symbol

            for np in net.connected:
                if isinstance(np, SubNet):
                    nets.append(cast(SubNet[T], np))
                elif isinstance(np, Net):
                    subname, subsymbol = flatten_net(np, ports, nets, shorts, tags)
                    if name is None:
                        name = subname
                    if symbol is None:
                        symbol = subsymbol
                    # If multiple *different* symbols are present, raise an error.
                    elif subsymbol is not None and symbol != subsymbol:
                        raise ValueError(
                            "Multiple different symbols assigned to one net"
                        )
                else:
                    ports.append(np)
        elif isinstance(net, TopologyNet):
            ports.extend(net.sequence)
        else:
            raise TypeError("Neither Net nor TopologyNet")

        # Add the current net's tags
        ntags = Tags.get(net)
        if ntags:
            for t in ntags.tags:
                if isinstance(t, BuiltinTag):
                    raise ValueError(
                        f"BuiltinTag {t.value} cannot be assigned to an object in the design"
                    )
            tags.update(ntags.tags)
    return name, symbol


def translate_provide(
    p: Provide,
    support: ppb2.Support,
    parent: Circuit | Component,
    into_design: dpb2.DesignV1,
    trace: Trace,
    restrict_info: RestrictInfo,
):
    support.bundle = translate_bundle(p.bundle, into_design)
    for opt in p.options:
        reqs: dict[Port, tuple[Circuit | Component, Restrictions | None]] = {}
        pbopt = support.options.add()
        for iface, port in opt:
            reqport = Provide.required_through(port) or port
            provider = Provide.provided_by(reqport)
            restrictions = Provide.restrictions_for(reqport)
            if provider:
                reqs[reqport] = (provider, restrictions)
            if Proxy.type(iface) is not Port:
                entries = (
                    (i, p)
                    for (i, p) in zip(
                        extract(iface, Port, through=(Port,)),
                        extract(port, Port, through=(Port,)),
                        strict=True,
                    )
                    if Proxy.type(i) is Port and Proxy.type(p) is Port
                )
            else:
                entries = ((iface, port),)
            for sub_iface, sub_port in entries:
                pbentry = pbopt.entries.add()
                pbentry.key.path.append(support.bundle)
                if sub_iface is not p.bundle:
                    idmap.request_local(pbentry.key, sub_iface, p.bundle)
                idmap.request_local(pbentry.value, sub_port, parent)
        if reqs:
            for reqport, (provider, restrictions) in reqs.items():
                if reqport not in idmap.parent_of:
                    idmap.set_parent(reqport, parent, None)
                # else:
                #     print(f"WARNING: Already set parent for {reqport}")
                pbreq = pbopt.requires.add()
                pbport = pbreq.port
                # pbport.name = pathstring(relativeref(path, circuit_path))
                # TODO
                pbport.name = "nested"
                pbport.id = mapped(id(reqport))
                translate_port_type(reqport, pbport.type, into_design)
                idmap.request_local(pbreq.instance, provider, parent, empty_ok=True)
                if restrictions:
                    translate_restricts(
                        restrictions, pbopt.restricts, parent, reqport, restrict_info
                    )

    idmap.set_parent(p, parent, trace)


# Make Restrictions hidden as a type.
def translate_restricts(
    restrictions: Restrictions,
    into_restricts: RepeatedCompositeFieldContainer[ppb2.Restrict],
    parent: Circuit | Component,
    required_bundle: Port,
    restrict_info: RestrictInfo,
):
    """
    Translate restrictions more efficiently by only checking candidate ports
    from relevant provides instead of all ports in the circuit.
    Uses caching to avoid redundant processing of identical restrictions.

    Args:
        restrictions: Mapping from restricted ports to restriction functions
        into_restricts: Protocol buffer container to add restrictions to
        parent: The parent circuit or component
        required_bundle: The bundle being required (used to find relevant provides)
    """

    for subport, restriction in restrictions.items():
        # Create cache key based on parent, bundle type, subport, and restriction function
        cache_key = (
            id(parent),
            type(required_bundle).__name__,
            id(subport),
            id(restriction),
        )

        if cache_key in _restriction_cache:
            # Use cached results
            into_restrict = into_restricts.add()
            idmap.request_local(into_restrict.port, subport, parent)
            into_restrict.index = _restriction_cache[cache_key]
            into_restrict.permit = True
            continue

        into_restrict = into_restricts.add()
        idmap.request_local(into_restrict.port, subport, parent)
        into_restrict.permit = True

        # Get candidate ports more efficiently
        candidate_ports = list(
            _get_candidate_ports_for_restriction(required_bundle, subport)
        )
        for port in candidate_ports:
            require_bund = Provide.required_through(port)
            if require_bund:
                raise ValueError(f"Nested requirement not supported: {require_bund}")

        # Cache the results for future use
        cache_index = len(_restriction_cache)
        _restriction_cache[cache_key] = cache_index
        into_restrict.index = cache_index

        restrict_entry = restrict_info.restricts.add()
        for port in candidate_ports:
            if restriction(port):
                idmap.request_local(restrict_entry.affected.add(), port, parent)


def _get_candidate_ports_for_restriction(
    required_bundle: Port, restricted_subport: Port
) -> Iterable[Port]:
    """
    Get candidate ports that could satisfy a restriction using BFS through proxy relationships.

    Args:
        parent: The parent circuit or component
        required_bundle: The bundle being required
        restricted_subport: The specific subport being restricted

    Returns:
        Iterable of candidate ports to check against the restriction
    """

    def single_ports(port: Port) -> Generator[Port]:
        for subport in extract(port, Port):
            if subport.is_single_pin():
                yield subport
            else:
                yield from single_ports(subport)

    # Get candidate ports by finding matching bundle types and corresponding subports
    required_bundle_type = Proxy.forkbase(required_bundle)
    candidate_ports = set()

    def get_candidates(bundle_port: Port, actual_port: Port):
        require_bund = Provide.required_through(actual_port)
        if require_bund is not None:
            # This actual_port is derived from a required bundle (nested requirement)
            # We need to recursively find candidates from the required bundle
            nested_candidates = _get_candidate_ports_for_restriction(
                require_bund, actual_port
            )
            candidate_ports.update(nested_candidates)

        # Always check correspondence for direct ports (whether required or not)
        elif _proxies_correspond(bundle_port, restricted_subport):
            candidate_ports.add(actual_port)

    provider = Provide.provided_by(required_bundle)
    for provide_instance in extract(provider, Provide):
        provide_bundle_type = Proxy.forkbase(provide_instance.bundle)
        # Filtered down provides for the target bundle base type
        if provide_bundle_type is required_bundle_type:
            for option in provide_instance.options:
                for bundle_port, actual_port in option:
                    if bundle_port.is_single_pin():
                        get_candidates(bundle_port, actual_port)
                    else:
                        # Bundle of ports, add nested single ports if corresponding.
                        for bundle_subport, actual_subport in zip(
                            single_ports(bundle_port),
                            single_ports(actual_port),
                            strict=True,
                        ):
                            get_candidates(bundle_subport, actual_subport)

    return candidate_ports


def _proxies_correspond(provide_bundle_port: Port, restricted_subport: Port) -> bool:
    """
    Check if two single ports correspond by tracing their proxy relationships.
    """

    if isinstance(provide_bundle_port, Proxy) and isinstance(restricted_subport, Proxy):
        return Proxy.of(provide_bundle_port) is Proxy.of(restricted_subport)
    return False


def get_symbol_component(symbol: Symbol) -> Component | None:
    """Get the parent Component of a symbol by traversing the parent hierarchy."""
    current = symbol
    while current is not None:
        parent = idmap.parent_of.get(current)
        if isinstance(parent, Component):
            return parent
        current = parent
    return None


def translate_signal_constraint(
    sc: SignalConstraint,
    into_module: mpb2.Module,
    into_design: dpb2.DesignV1,
    circuit: Circuit,
    trace: Trace,
):
    for t, bc in visit(sc, BaseConstrain, path=trace.path):
        translate_constrain(bc, into_module, into_design, circuit, t)


def translate_constrain(
    bc: BaseConstrain,
    into_module: mpb2.Module,
    into_design: dpb2.DesignV1,
    circuit: Circuit,
    trace: Trace,
):
    if isinstance(bc, BaseConstrainPairwise):
        for tref, t in bc._pairwise():
            for pc in bc._pairwise_constraints:
                if isinstance(pc, TimingDifferenceConstraint):
                    into_constraint = into_module.constrain_timing_differences.add()
                    translate_port_mapping(
                        tref.begin, tref.end, into_constraint.path1, circuit
                    )
                    translate_port_mapping(
                        t.begin, t.end, into_constraint.path2, circuit
                    )

                    into_constraint.constraint.min_delta = pc.min_delta
                    into_constraint.constraint.max_delta = pc.max_delta
        if isinstance(bc, ConstrainDiffPair) and bc._structure:
            for t in bc.topologies:
                translate_differential_routing_structure_constraint(
                    bc._structure,
                    t.begin,
                    t.end,
                    into_design,
                    into_module.differential_structures.add(),
                    circuit,
                    trace.path,
                )

    for t in bc._individual():
        for c in bc._constraints:
            if isinstance(c, TimingConstraint):
                into_constraint = into_module.constrain_timings.add()
                translate_port_mapping(t.begin, t.end, into_constraint.path, circuit)
                into_constraint.constraint.min_delay = c.min_delay
                into_constraint.constraint.max_delay = c.max_delay
            elif isinstance(c, InsertionLossConstraint):
                into_constraint = into_module.constrain_insertion_losses.add()
                translate_port_mapping(t.begin, t.end, into_constraint.path, circuit)
                into_constraint.constraint.min_loss = c.min_loss
                into_constraint.constraint.max_loss = c.max_loss

    if isinstance(bc, Constrain) and bc._structure:
        for t in bc.topologies:
            translate_routing_structure_constraint(
                bc._structure,
                t.begin,
                t.end,
                into_design,
                into_module.structures.add(),
                circuit,
                trace.path,
            )


def translate_circuit(
    circuit: Circuit,
    into_design: dpb2.DesignV1,
    circuit_path: RefPath,
    status: InstanceStatus,
    restrict_info: RestrictInfo,
):
    # CAUTION: If circuits are memoized, modifying circuits _outside_ it will
    # break as soon as multiple instances of the same circuit are present in
    # the design. As of this writing, the routing structure layer net
    # association modify outer nets.

    into_module = into_design.modules.add()
    into_module.name = type(circuit).__name__

    # if multiple nets are present in a module that reference each other, we
    # need to flatten them.
    collected_nets: dict[Net, Trace] = {}
    topology_nets: dict[TopologyNet, Trace] = {}

    with dispatch(circuit, base_path=circuit_path) as d:

        @d.register
        def _(subcircuit: Circuit, trace: Trace):
            subcircuit_status = InstanceStatus(
                in_bom=subcircuit.in_bom
                if subcircuit.in_bom is not None
                else status.in_bom,
                soldered=subcircuit.soldered
                if subcircuit.soldered is not None
                else status.soldered,
                schematic_x_out=subcircuit.schematic_x_out
                if subcircuit.schematic_x_out is not None
                else status.schematic_x_out,
            )
            mod_id = translate_circuit(
                subcircuit, into_design, trace.path, subcircuit_status, restrict_info
            )
            inst = into_module.instances.add()
            inst.name = pathstring(relativeref(trace.path, circuit_path))
            inst.id = mapped(id(subcircuit))
            inst.instantiable = mod_id
            idmap.set_parent(subcircuit, circuit, trace)
            if subcircuit.transform:
                place = subcircuit.transform
                if trace.transform:
                    place = trace.transform * place
                assert isinstance(place, Placement)
                instpose = into_module.instance_poses.add()
                # TODO anchor
                instpose.side = translate_side(place.side)
                translate_pose(place, instpose.pose)
                idmap.request_local(instpose.instance, subcircuit, circuit)

        @d.register
        def _(component: Component, trace: Trace):
            idmap.set_parent(component, circuit, trace)
            comp_id = translate_component(
                component, into_design, trace.path, restrict_info
            )
            inst = into_module.instances.add()
            inst.name = pathstring(relativeref(trace.path, circuit_path))
            inst.id = mapped(id(component))
            inst.instantiable = comp_id
            translate_file_info(inst.info, component)

            if component.transform:
                place = component.transform
                if trace.transform:
                    place = trace.transform * place
                assert isinstance(place, Placement)
                instpose = into_module.instance_poses.add()
                instpose.side = translate_side(place.side)
                translate_pose(place, instpose.pose)
                idmap.request_local(instpose.instance, component, circuit)
            if component.reference_designator:
                into_ref = into_module.reference_designators.add()
                idmap.request_local(into_ref.instance, component, circuit)
                into_ref.reference = component.reference_designator
            inststatus = into_module.instance_statuses.add()
            inststatus.instance.path.append(inst.id)
            inststatus.in_bom = (
                component.in_bom if component.in_bom is not None else status.in_bom
            )
            inststatus.soldered = (
                component.soldered
                if component.soldered is not None
                else status.soldered
            )
            inststatus.schematic_x_out = (
                component.schematic_x_out
                if component.schematic_x_out is not None
                else status.schematic_x_out
            )

        @d.register
        def _(ip: InstancePlacement, trace: Trace):
            instpose = into_module.instance_poses.add()
            instpose.side = translate_side(ip.placement.side)
            translate_pose(ip.placement, instpose.pose)
            instance = ip.instance()
            if not instance:
                cls = circuit.__class__
                raise UserCodeException(
                    f"A placement in {cls.__module__}.{cls.__name__} is referencing an object that no longer exists."
                )
            relative_to = None
            if ip.relative_to:
                relative_to = ip.relative_to()
                if not relative_to:
                    cls = circuit.__class__
                    raise UserCodeException(
                        f"A placement in {cls.__module__}.{cls.__name__} is referencing an object that no longer exists."
                    )

            idmap.request_local(instpose.instance, instance, circuit)
            if relative_to:
                idmap.request_local(instpose.anchor, relative_to, circuit)

        @d.register
        def _(feature: Feature, trace: Trace):
            translate_feature(feature, into_module.layers.add, trace.transform)

        @d.register
        def _(port: Port, trace: Trace):
            rq = Provide.required_through(port) or port
            provider = Provide.provided_by(rq)
            if provider is not None:
                raise UserCodeException(
                    f"Port {pathstring(trace.path)} is a required port from {provider} and should not be a member field of a circuit",
                    hint="Ports required from a provider can be included in nets within this circuit, but it's not a port that the circuit itself exposes, and should not be set as a field on the object directly.",
                )

            pbport = into_module.ports.add()
            pbport.name = pathstring(relativeref(trace.path, circuit_path))
            pbport.id = mapped(id(port))
            translate_port_type(port, pbport.type, into_design)
            idmap.set_parent(port, circuit, trace)

        @d.register
        def _(nc: _NoConnect, trace: Trace):
            idmap.request_local(into_module.no_connects.add(), nc.port, circuit)

        @d.register
        def _(c: Copper, trace: Trace):
            # Handled in the net translation
            # TODO: Ensure that it is on a net
            pass

        @d.register
        def _(v: Via, trace: Trace):
            # Handled in the net translation
            # TODO: Ensure that it is on a net
            pass

        @d.register
        def _(net: Net, trace: Trace):
            collected_nets[net] = trace

        @d.register
        def _(p: Provide, trace: Trace):
            translate_provide(
                p,
                into_module.supports.add(),
                circuit,
                into_design,
                trace,
                restrict_info,
            )

        @d.register
        def _(bpm: BridgingPinModel, trace: Trace):
            pm = into_module.pin_models.add()
            a, b = bpm.ports
            idmap.request_local(pm.a, a, circuit)
            idmap.request_local(pm.b, b, circuit)
            translate_pin_model(bpm, pm.pin_model)

        @d.register
        def _(tpm: TerminatingPinModel, trace: Trace):
            pm = into_module.pin_models.add()
            idmap.request_local(pm.a, tpm.port, circuit)
            translate_pin_model(tpm, pm.pin_model)

        @d.register
        def _(a: Annotation, trace: Trace):
            into_module.annotations.append(a.text)

        @d.register
        def _(p: PortAttachment, trace: Trace):
            into_net_geom = into_module.net_geoms.add()
            idmap.request_local(into_net_geom.ref, p.port, circuit)
            obj = p.attachment
            if isinstance(obj, Copper):
                translate_copper(obj, into_net_geom.geom)
            elif isinstance(obj, Via):
                translate_via(obj, into_net_geom.geom)

        # RefLabels

        # ValueLabels

        # SameSchematicGroups, LayoutGroups, SameLayoutGroups
        @d.register
        def _(group: SchematicGroup, trace: Trace):
            group_name = str(trace.path[-1])
            if len(group.elems) == 0:
                into_group = into_module.schematic_groups.add()
                into_group.group = group_name

            def process_schematic_element(elem, path_context: str):
                if isinstance(elem, Symbol):
                    # Get the parent component that this symbol comes from
                    parent_component = get_symbol_component(elem)
                    if not parent_component:
                        raise ValueError(
                            f"Schematic group at {path_context} references symbol with no parent component"
                        )
                    component_symbols = list(extract(parent_component, Symbol))
                    into_group.unit = component_symbols.index(elem)
                    idmap.request_local(into_group.instance, parent_component, circuit)
                else:
                    # For Circuit or Component elements
                    idmap.request_local(into_group.instance, elem, circuit)

            for elem in group.elems:
                into_group = into_module.schematic_groups.add()
                into_group.group = group_name

                if isinstance(elem, Container):
                    # Extract meaningful elements from the Container (circuits, components, and symbols)
                    meaningful_elements = list(
                        extract(elem, (Circuit, Component, Symbol))
                    )
                    if not meaningful_elements:
                        raise ValueError(
                            f"Schematic group at {pathstring(trace.path)} contains Container with no "
                            f"Circuit, Component, or Symbol. Container must contain at least one of these types."
                        )
                    # Process each meaningful element found in the Container
                    for meaningful_elem in meaningful_elements:
                        process_schematic_element(
                            meaningful_elem, pathstring(trace.path)
                        )
                else:
                    process_schematic_element(elem, pathstring(trace.path))

        # SchematicGroupOrder

        @d.register
        def _(t: TopologyNet, trace: Trace):
            for port1, port2 in zip(t.sequence, t.sequence[1:], strict=False):
                translate_port_mapping(
                    port1, port2, into_module.topology_segments.add(), circuit
                )
            # TopologyNet implies Net.
            topology_nets[t] = trace

        @d.register
        def _(bc: BaseConstrain, trace: Trace):
            translate_constrain(bc, into_module, into_design, circuit, trace)

        @d.register
        def _(sc: SignalConstraint, trace: Trace):
            translate_signal_constraint(sc, into_module, into_design, circuit, trace)

    def process_net(net: Net | TopologyNet, trace: Trace):
        pbnet = into_module.nets.add()
        flattags = set()
        flatports = []
        flatnets = []
        flatshorts = []
        flatname, flatsymbol = flatten_net(
            net, flatports, flatnets, flatshorts, flattags
        )
        pbnet.id = mapped(id(net))
        idmap.set_parent(net, circuit, trace)
        if flatname is not None:
            pbnet.name = flatname
        if flatsymbol is not None:
            symbol_id = translate_symbol(flatsymbol, into_design, trace.path)
            _, *excess = decompose(flatsymbol, Pin)
            if len(excess) > 0:
                raise UserCodeException(
                    f"Symbol {Proxy.type(flatsymbol).__name__} on Net {pathstring(trace.path)} has multiple pins"
                )
            if isinstance(net, Net):
                checkports = net.connected
            elif isinstance(net, TopologyNet):
                checkports = net.sequence
            port_type = _match_port_type(checkports, net)
            if port_type is not None and port_type is not _PORT:
                raise ValueError(
                    f"Cannot set symbol on bundle net {pathstring(trace.path)} with ports of type {port_type.__class__.__name__}"
                )
            pbnet_symbol = into_module.net_symbols.add()
            pbnet_symbol.net.path.append(pbnet.id)
            pbnet_symbol.symbol = symbol_id
        if flattags:
            into_apply_tag = into_module.apply_tags.add()
            into_apply_tag.local.path.append(pbnet.id)
            for tag in flattags:
                translate_user_tag(tag, into_apply_tag.tags.add())
        if isinstance(net, Net):
            for p in extract(net.port, SubNet, through=(SubNet,), refs=True):
                if tagged := Tags.get(p):
                    into_apply_tag = into_module.apply_tags.add()
                    into_apply_tag.local.path.append(pbnet.id)
                    idmap.request_local(
                        into_apply_tag.local, p._subnetport, net._port._subnetport
                    )
                    for tag in tagged.tags:
                        translate_user_tag(tag, into_apply_tag.tags.add())
        if flatports:
            for port in flatports:
                # traverse port aliases.
                while Proxy.is_ref(port):
                    port = Proxy.of(port)
                if isinstance(port, Copper):
                    into_net_geom = into_module.net_geoms.add()
                    idmap.request_local(into_net_geom.ref, net, circuit)
                    translate_copper(port, into_net_geom.geom)
                elif isinstance(port, Via):
                    into_net_geom = into_module.net_geoms.add()
                    idmap.request_local(into_net_geom.ref, net, circuit)
                    translate_via(port, into_net_geom.geom)
                else:
                    idmap.request_local(pbnet.refs.add(), port, circuit)
                    reqport = Provide.required_through(port) or port
                    provider = Provide.provided_by(reqport)
                    restrictions = Provide.restrictions_for(reqport)
                    if provider:
                        if not idmap.visited(id(reqport)):
                            idmap.set_parent(reqport, circuit, None)

                            pbreq = into_module.requires.add()
                            pbport = pbreq.port
                            pbport.name = pathstring(
                                relativeref(trace.path, circuit_path)
                            )
                            pbport.id = mapped(id(reqport))
                            translate_port_type(reqport, pbport.type, into_design)
                            idmap.request_local(
                                pbreq.instance, provider, circuit, empty_ok=True
                            )

                            if restrictions:
                                translate_restricts(
                                    restrictions,
                                    into_module.restricts,
                                    circuit,
                                    reqport,
                                    restrict_info,
                                )

            first = flatports[0]
            translate_port_type(first, pbnet.type, into_design)
        for flatnet in flatnets:
            ref = pbnet.refs.add()
            if isinstance(flatnet, SubNet):
                idmap.request_local(ref, flatnet._base, circuit)
                idmap.request_local(
                    ref, flatnet._subnetport, flatnet._base._port._subnetport
                )
            else:
                idmap.request_local(ref, flatnet, circuit)

        for flatshort in flatshorts:
            for p1, p2 in zip(
                flatshort.connected, flatshort.connected[1:], strict=False
            ):
                into_short = into_module.short_traces.add()
                idmap.request_local(into_short.key, p1, circuit)
                idmap.request_local(into_short.value, p2, circuit)

    ordered_nets = nets_leaves_to_root(collected_nets)
    for net, trace in ordered_nets:
        process_net(net, trace)
    for net, trace in topology_nets.items():
        process_net(net, trace)

    ### File Info
    translate_file_info(into_module.info, circuit)

    mod_id = idmap.unique()
    into_module.id = mod_id
    return mod_id


def nets_leaves_to_root(nets: dict[Net, Trace]) -> Iterable[tuple[Net, Trace]]:
    """Return nets in order from leaves to root (dependency order)."""
    visited = set()

    def visit(net: Net, trace: Trace) -> Iterable[tuple[Net, Trace]]:
        if net in visited or idmap.visited(id(net)):
            return
        visited.add(net)

        # Visit dependencies first (leaves)
        for connected in net.connected:
            if isinstance(connected, Net):
                if connected in nets:
                    yield from visit(connected, nets[connected])
                else:
                    # We don't get traces for nets found outside the dispatch,
                    # so we use the trace of the net we're visiting.
                    yield from visit(connected, trace)

        # Then yield this net (root)
        yield net, trace

    for net, trace in nets.items():
        yield from visit(net, trace)
