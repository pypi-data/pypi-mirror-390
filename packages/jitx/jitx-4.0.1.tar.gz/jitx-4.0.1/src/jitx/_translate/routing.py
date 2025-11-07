import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.diff_routing_pb2 as drpb2
import jitxcore._proto.routing_pb2 as rpb2
import jitxcore._proto.routing_structures_pb2 as rspb2

from jitx._structural import RefPath
from jitx._translate.feature import translate_feature_type
from jitx._translate.fileinfo import translate_file_info
from jitx._translate.layerindex import translate_layer_index
from jitx._translate.mapping import translate_port_mapping
from jitx._translate.via import translate_fence_via
from jitx.circuit import Circuit
from jitx.error import UserCodeException
from jitx.inspect import extract
from jitx.net import DiffPair, Net, Port
from jitx.shapes.primitive import Empty
from jitx.si import (
    DifferentialRoutingStructure,
    DifferentialRoutingStructureConstraint,
    RefLayerType,
    RoutingStructure,
    RoutingStructureConstraint,
    _AddGeom,
    _RefLayer,
    _StructureViaFence,
)

from .dispatch import Trace, dispatch, queue_dispatch
from .idmap import idmap


class RefLayerNet:
    """Associate a net for a routing structure reference layer."""

    layer: int
    ref: Net

    def __init__(self, layer: int, ref: Net):
        self.layer = layer
        self.ref = ref


def translate_nets_into_structure(
    structure: RoutingStructureConstraint | DifferentialRoutingStructureConstraint,
    circuit: Circuit,
    into_structure: rspb2.Structure | rspb2.DifferentialStructure,
):
    virtual_nets: dict[Net, Net] = {}

    def virtual_net(net: RefLayerType) -> Net:
        nonlocal circuit
        if net in virtual_nets:
            return virtual_nets[net]
        else:
            virtual: Net[Port] = Net()
            net.connected.append(virtual)
            queue_dispatch(circuit, virtual)
            virtual_nets[net] = virtual
            return virtual

    for layer, net in structure.ref_layers.items():
        net = virtual_net(net)
        translate_ref_layer_net(
            RefLayerNet(layer, net), into_structure.ref_layer_nets.add(), circuit
        )

    for lid, structlayer in structure.structure.layers.items():
        for fence in extract(structlayer, _StructureViaFence):
            rl = fence.reference_layer
            if rl is None:
                raise ValueError("Unexpected missing reference layer for via fence")
            net = structure.ref_layers.get(rl)
            if net is None:
                raise ValueError("Unexpected missing reference layer net for via fence")
            net = virtual_net(net)
            # fence layer nets are the layer _of the route_, hence we look at "lid" here.
            translate_ref_layer_net(
                RefLayerNet(lid, net), into_structure.via_fence_nets.add(), circuit
            )


def translate_structure_via_fence(
    fence: _StructureViaFence,
    into_layer: rpb2.RoutingLayer | drpb2.DifferentialRoutingLayer,
):
    if fence._inverted:
        from jitx._translate.design import DesignTranslationContext

        # the routing layer was inverted, make sure the via definition can be "flipped".
        start = fence.definition.start_layer
        end = fence.definition.stop_layer
        nCu = len(
            DesignTranslationContext.require().design.substrate.stackup.conductors
        )
        if start < 0:
            start = start + nCu
        if end > 0:
            end = end - nCu
        if -start - 1 != end:
            raise UserCodeException(
                "Can only symmetrize via fences that use symmetric vias",
                hint="Make sure the via definition is symmetric around the center of the stackup, such as a through-hole via, when creating symmetric routing structures.",
            )
    translate_fence_via(fence, into_layer.fence)


def translate_routing_structure_constraint(
    structure: RoutingStructureConstraint,
    port1: Port,
    port2: Port,
    into_design: dpb2.DesignV1,
    into_structure: rspb2.Structure,
    circuit: Circuit,
    path: RefPath,
):
    translate_port_mapping(port1, port2, into_structure.path, circuit)
    into_structure.routing_structure = translate_routing_structure(
        structure.structure, into_design.routings.add(), path
    )
    translate_nets_into_structure(structure, circuit, into_structure)


def translate_differential_routing_structure_constraint(
    structure: DifferentialRoutingStructureConstraint,
    port1: DiffPair,
    port2: DiffPair,
    into_design: dpb2.DesignV1,
    into_structure: rspb2.DifferentialStructure,
    circuit: Circuit,
    path: RefPath,
):
    # Check if ports are DiffPair instances for safe 'p' and 'n' access
    if not isinstance(port1, DiffPair) or not isinstance(port2, DiffPair):
        raise TypeError("Expected DiffPair objects for timing_difference_constraint")

    translate_port_mapping(port1.p, port2.p, into_structure.path1, circuit)
    translate_port_mapping(port1.n, port2.n, into_structure.path2, circuit)
    into_structure.differential_routing_structure = (
        translate_differential_routing_structure(
            structure.structure,
            into_design,
            into_design.differential_routings.add(),
            path,
        )
    )

    translate_nets_into_structure(structure, circuit, into_structure)


def translate_routing_structure(
    routing: RoutingStructure, into_routing: rpb2.Routing, path: RefPath
):
    into_routing.name = type(routing).__name__
    for index, layer in routing.layers.items():
        translate_routing_layer(layer, index, into_routing.layers.add(), path)

    translate_file_info(into_routing.info, routing)

    routing_id = idmap.unique()
    into_routing.id = routing_id
    return routing_id


def translate_routing_layer(
    layer: RoutingStructure.Layer,
    index: int,
    into_layer: rpb2.RoutingLayer,
    path: RefPath,
):
    translate_layer_index(index, into_layer.layer)
    into_layer.trace_width = layer.trace_width
    into_layer.velocity = layer.velocity
    into_layer.insertion_loss = layer.insertion_loss
    if layer.clearance is not None:
        into_layer.clearance = layer.clearance
    if layer.neck_down is not None:
        translate_neck_down(layer.neck_down, into_layer.neck_down)
    with dispatch(layer, base_path=path) as d:

        @d.register
        def _(ref_layer: _RefLayer, path: RefPath):
            translate_ref_layer(ref_layer, into_layer.ref_layers.add())

        @d.register
        def _(add_geom: _AddGeom, path: RefPath):
            translate_add_geom(add_geom, into_layer.add_geoms.add())

        @d.register
        def _(fence: _StructureViaFence, trace: Trace):
            translate_structure_via_fence(fence, into_layer)


def translate_neck_down(
    neck_down: RoutingStructure.NeckDown, into_neck_down: rpb2.NeckDown
):
    if neck_down.trace_width is not None:
        into_neck_down.trace_width = neck_down.trace_width
    if neck_down.clearance is not None:
        into_neck_down.clearance = neck_down.clearance
    if neck_down.insertion_loss is not None:
        into_neck_down.insertion_loss = neck_down.insertion_loss
    if neck_down.velocity is not None:
        into_neck_down.velocity = neck_down.velocity


def translate_ref_layer(ref_layer: _RefLayer, into_ref_layer: rspb2.RefLayer):
    translate_layer_index(ref_layer.layer, into_ref_layer.layer)
    into_ref_layer.desired_width = ref_layer.desired_width
    # if ref_layer.required_width is not None:
    #    into_ref_layer.required_width = ref_layer.required_width


def translate_add_geom(add_geom: _AddGeom, into_add_geom: rspb2.AddGeom):
    if not isinstance(add_geom.feature.shape, Empty):
        raise UserCodeException(
            "Routing Structure geometry should not have a shape",
            hint="Use .geometry() to add geometry to a Routing Structure",
        )
    translate_feature_type(add_geom.feature, lambda: into_add_geom.layer)
    into_add_geom.desired_width = add_geom.width


def translate_differential_routing_structure(
    routing: DifferentialRoutingStructure,
    into_design: dpb2.DesignV1,
    into_routing: drpb2.DifferentialRouting,
    path: RefPath,
):
    into_routing.name = type(routing).__name__
    if routing.uncoupled_region is not None:
        into_routing.uncoupled_region = translate_routing_structure(
            routing.uncoupled_region, into_design.routings.add(), path
        )

    for index, layer in routing.layers.items():
        translate_differential_routing_layer(
            layer, index, into_routing.layers.add(), path
        )

    translate_file_info(into_routing.info, routing)

    routing_id = idmap.unique()
    into_routing.id = routing_id
    return routing_id


def translate_differential_routing_layer(
    layer: DifferentialRoutingStructure.Layer,
    index: int,
    into_layer: drpb2.DifferentialRoutingLayer,
    path: RefPath,
):
    translate_layer_index(index, into_layer.layer)
    into_layer.trace_width = layer.trace_width
    into_layer.velocity = layer.velocity
    into_layer.insertion_loss = layer.insertion_loss
    into_layer.pair_spacing = layer.pair_spacing
    if layer.clearance is not None:
        into_layer.clearance = layer.clearance
    if layer.neck_down is not None:
        translate_differential_neck_down(layer.neck_down, into_layer.neck_down)
    with dispatch(layer, base_path=path) as d:

        @d.register
        def _(ref_layer: _RefLayer, trace: Trace):
            translate_ref_layer(ref_layer, into_layer.ref_layers.add())

        @d.register
        def _(add_geom: _AddGeom, trace: Trace):
            translate_add_geom(add_geom, into_layer.add_geoms.add())

        @d.register
        def _(fence: _StructureViaFence, trace: Trace):
            translate_structure_via_fence(fence, into_layer)


def translate_differential_neck_down(
    neck_down: RoutingStructure.NeckDown, into_neck_down: drpb2.DifferentialNeckDown
):
    if neck_down.trace_width is not None:
        into_neck_down.trace_width = neck_down.trace_width
    if neck_down.clearance is not None:
        into_neck_down.clearance = neck_down.clearance
    if neck_down.insertion_loss is not None:
        into_neck_down.insertion_loss = neck_down.insertion_loss
    if neck_down.velocity is not None:
        into_neck_down.velocity = neck_down.velocity
    if isinstance(neck_down, DifferentialRoutingStructure.NeckDown):
        if neck_down.pair_spacing is not None:
            into_neck_down.pair_spacing = neck_down.pair_spacing


def translate_ref_layer_net(
    ref_layer_net: RefLayerNet, into_ref_layer_net: rspb2.RefLayerNet, circuit: Circuit
):
    translate_layer_index(ref_layer_net.layer, into_ref_layer_net.layer)
    idmap.request_local(into_ref_layer_net.ref, ref_layer_net.ref, circuit)
