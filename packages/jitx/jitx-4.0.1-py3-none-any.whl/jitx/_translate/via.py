from jitx import current
from jitx._structural import Proxy
from jitx.error import UserCodeException
from jitx.inspect import decompose
from jitx.layerindex import Side
from jitx.constraints import (
    FenceVia,
    SquareViaStitchGrid,
    StitchVia,
    TriangularViaStitchGrid,
)
from jitx.si import PinModel
from jitx.stackup import Conductor
from jitx.via import Backdrill, BackdrillSet, Via, ViaDiameter

from .idmap import mapped
from .layerindex import translate_layer_index
from .enums import translate_via_drill_type
from .fileinfo import translate_file_info
from .signal_models import translate_pin_model

import jitxcore._proto.via_pb2 as vpb2
import jitxcore._proto.via_patterns_pb2 as vppb2
import jitxcore._proto.geom_pb2 as gpb2
from jitxcore._proto.enums_pb2 import TentMode


def translate_tented(side: set[Side] | Side | None | bool):
    if side is True or side is None:
        return TentMode.TENT_BOTH
    elif side is False:
        return TentMode.TENT_NONE
    elif side == 0:
        return TentMode.TENT_TOP
    elif side == -1:
        return TentMode.TENT_BOTTOM
    elif isinstance(side, set):
        if len(side) == 1:
            return translate_tented(next(iter(side)))
        elif len(side) == 2 and side == {Side.Top, Side.Bottom}:
            return TentMode.TENT_BOTH
        else:
            raise Exception("Bad via tented value:", side)
    else:
        raise Exception("Bad via tented value:", side)


def translate_backdrill_set(
    backdrill: BackdrillSet | Backdrill | None, into: vpb2.BackdrillSet
):
    if backdrill is None:
        return

    if isinstance(backdrill, Backdrill):
        translate_backdrill(backdrill, into.bottom)
    else:
        translate_backdrill(backdrill.top, into.top)
        translate_backdrill(backdrill.bottom, into.bottom)


def translate_backdrill(backdrill: Backdrill | None, into: vpb2.Backdrill):
    if backdrill is None:
        return
    into.diameter = backdrill.diameter
    into.startpad_diameter = backdrill.startpad_diameter
    into.solder_mask_opening = backdrill.solder_mask_opening
    into.copper_clearance = backdrill.copper_clearance


def translate_via_type(via: type[Via], into: vpb2.Via):
    via_id = mapped(id(via))
    into.id = via_id
    into.name = via.__name__
    into.type = translate_via_drill_type(via.type)
    translate_layer_index(via.start_layer, into.start)
    translate_layer_index(via.stop_layer, into.stop)

    translate_via_diameter(via.diameter, into)
    if via.diameters:
        check_wellformed_via_stack(via.diameters)
        translate_via_stack(via.diameters, into)

    into.hole_diameter = via.hole_diameter
    into.filled = via.filled
    into.tented = translate_tented(via.tented)
    into.via_in_pad = via.via_in_pad
    for layers, model in via.models.items():
        translate_structure_model(
            layers[0], layers[1], model, into.structure_models.add()
        )
    translate_backdrill_set(via.backdrill, into.backdrill)
    translate_file_info(into.info, via)
    return via_id


# Conditions to check:
# 1. Check that all referenced layers exist in the via (start_layer to stop_layer).
# 2. Check that the same layer is not referenced in several entries of the via stack.
def check_wellformed_via_stack(
    via_stack: dict[int | tuple[int, ...], float | ViaDiameter],
):
    # TODO: Should we cache `copper_layer_count` in `current`?
    conductors = list(decompose(current.substrate.stackup, Conductor))
    copper_layer_count = len(conductors)

    def stack_layers(key: int | tuple[int, ...]) -> tuple[int, ...]:
        if isinstance(key, tuple):
            return key
        else:
            return (key,)

    def other_representation(layer: int) -> int:
        # Layers are counted up from 0 as the top layer.
        if layer >= 0:
            # Count layers down from -1 as the bottom layer.
            return layer - copper_layer_count
        # Layers are counted down from -1 as the bottom layer.
        else:
            # Count layers up from 0 as the top layer.
            return layer + copper_layer_count

    def check_layers_exist_in_stackup():
        for key in via_stack.keys():
            for layer in stack_layers(key):
                if not (-copper_layer_count <= layer < copper_layer_count):
                    raise UserCodeException(
                        f"Conducting layer {layer} is referenced in a `Via.diameters` entry but does not exist in the design substrate stackup which has {copper_layer_count} conducting layers.",
                        hint=f"Make sure all layers in Via.diameters are integers in [-{copper_layer_count}, {copper_layer_count - 1}]",
                    )

    def check_layers_referenced_once():
        layers = set()
        for key in via_stack.keys():
            for layer in stack_layers(key):
                if layer in layers:
                    raise UserCodeException(
                        f"Layer {layer} is referenced more than once in a `Via.diameters` entry",
                        hint="Remove the duplicated layer from one of the `Via.diameters` entries.",
                    )
                other = other_representation(layer)
                if other in layers:
                    raise UserCodeException(
                        f"Layer {layer} and {other} represent the same layer in the {copper_layer_count}-layer board and are both referenced in a `Via.diameters` entry.",
                        hint=f"Remove either {layer} or {other} from the `Via.diameters` entries.",
                    )
                layers.add(layer)

    check_layers_exist_in_stackup()
    check_layers_referenced_once()


def translate_via_diameter(via_diameter: float | ViaDiameter, into: vpb2.Via):
    if isinstance(via_diameter, ViaDiameter):
        into.diameter = via_diameter.pad
        if via_diameter.nfp:
            into.nfp_diameter = via_diameter.nfp
    else:
        into.diameter = via_diameter


def translate_via_stack(
    via_stack: dict[int | tuple[int, ...], float | ViaDiameter], into: vpb2.Via
):
    for key, via_diameter in via_stack.items():
        into_via_diameter = into.diameters.add()
        if isinstance(key, tuple):
            for layer in key:
                translate_layer_index(layer, into_via_diameter.layers.add())
        else:
            translate_layer_index(key, into_via_diameter.layers.add())
        if isinstance(via_diameter, ViaDiameter):
            into_via_diameter.pad = via_diameter.pad
            if via_diameter.nfp:
                into_via_diameter.nfp = via_diameter.nfp
        else:
            into_via_diameter.pad = via_diameter


def translate_via(v: Via, into_geom: gpb2.Geom):
    into_via = into_geom.via
    into_via.via = Proxy.type(v).__name__
    pt = into_via.point
    if v.transform:
        pt.x, pt.y = v.transform._translate
    else:
        pt.x, pt.y = 0.0, 0.0
    # No properties have been applied.


def translate_structure_model(
    start: int, stop: int, model: PinModel, into: vpb2.StructureModel
):
    translate_layer_index(start, into.entry)
    translate_layer_index(stop, into.exit)
    translate_pin_model(model, into.model)


def translate_stitch_via(sv: StitchVia, into: vppb2.StitchVia):
    """Translate a StitchVia constraint to protobuf format."""
    into.definition = sv.definition.__name__

    if isinstance(sv.pattern, SquareViaStitchGrid):
        into.pattern.square.pitch = sv.pattern.pitch
        into.pattern.square.inset = sv.pattern.inset
    elif isinstance(sv.pattern, TriangularViaStitchGrid):
        into.pattern.triangular.pitch = sv.pattern.pitch
        into.pattern.triangular.inset = sv.pattern.inset
    else:
        raise ValueError(f"Unknown via stitch pattern type: {type(sv.pattern)}")


def translate_fence_via(fv: FenceVia, into: vppb2.FenceVia):
    into.definition = fv.definition.__name__
    into.pattern.pitch = fv.pattern.pitch
    into.pattern.offset = fv.pattern.offset
    if fv.pattern.num_rows is not None:
        into.pattern.num_rows = fv.pattern.num_rows
    if fv.pattern.min_pitch is not None:
        into.pattern.min_pitch = fv.pattern.min_pitch
    if fv.pattern.max_pitch is not None:
        into.pattern.max_pitch = fv.pattern.max_pitch
    if fv.pattern.initial_offset is not None:
        into.pattern.initial_offset = fv.pattern.initial_offset
    if fv.pattern.input_shape_only is not None:
        into.pattern.input_shape_only = fv.pattern.input_shape_only
