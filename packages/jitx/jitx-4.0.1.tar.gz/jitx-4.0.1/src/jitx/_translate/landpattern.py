from jitx._translate.fileinfo import translate_file_info
from jitx._translate.layerindex import translate_layer_index
from jitx.error import UserCodeException
from jitx.feature import Cutout, Feature
from jitx.shapes import Shape
from jitx.landpattern import Landpattern, Pad, PadShape
from jitx._structural import Proxy, RefPath, fieldref, relativeref, pathstring
from jitx.model3d import Model3D
from jitx.placement import Placement
from jitx.inspect import Trace, decompose

import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.enums_pb2 as epb2
import jitxcore._proto.landpattern_pb2 as lpb2
import jitxcore._proto.pad_pb2 as ppb2


from jitx.stackup import Conductor
from jitx.transform import IDENTITY

from .idmap import mapped, idmap, memoizer
from .feature import translate_feature
from .shape import translate_pose, translate_shape
from .enums import translate_side
from .dispatch import dispatch
from .. import current

from typing import Any


@memoizer
def translate_pad(pad: Pad, into_design: dpb2.DesignV1, path: RefPath):
    into_pad = into_design.pads.add()
    into_pad.name = Proxy.type(pad).__name__

    cutouts = tuple(decompose(pad, Cutout))
    into_pad.type = epb2.PadType.TH if cutouts else epb2.PadType.SMD

    translate_pad_shape(pad.shape, into_pad)
    if pad.shapes:
        check_wellformed_pad_stack(pad.shapes, into_pad.type)
        translate_pad_stack(pad.shapes, into_pad)

    with dispatch(pad, base_path=path) as d:

        @d.register
        def _(feature: Feature, trace: Trace):
            translate_feature(feature, into_pad.layers.add, trace.transform)

    # pad edge (boolean)

    translate_file_info(into_pad.info, pad)

    pad_id = idmap.unique()
    into_pad.id = pad_id
    return pad_id


# Conditions to check:
# 1. Pad shapes must only be provided for through-hole pads.
# 2. Check that all referenced layers exist in the design substrate stackup (-copper_layer_count <= layer < copper_layer_count).
# 3. Check that the same layer is not referenced in several entries of the pad stack.
def check_wellformed_pad_stack(
    pad_stack: dict[int | tuple[int, ...], Shape | PadShape], pad_type: epb2.PadType
):
    if pad_type == epb2.PadType.SMD:
        raise UserCodeException(
            "Pad shapes must only be provided for through-hole pads.",
            hint="Remove Pad.shapes or add a `Cutout` to the pad.",
        )

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
        for key in pad_stack.keys():
            for layer in stack_layers(key):
                if not (-copper_layer_count <= layer < copper_layer_count):
                    raise UserCodeException(
                        f"Conducting layer {layer} is referenced in a `Pad.shapes` entry but does not exist in the design substrate stackup which has {copper_layer_count} conducting layers.",
                        hint=f"Make sure all layers in Pad.shapes are integers in [-{copper_layer_count}, {copper_layer_count - 1}]",
                    )

    def check_layers_referenced_once():
        layers = set()
        for key in pad_stack.keys():
            for layer in stack_layers(key):
                if layer in layers:
                    raise UserCodeException(
                        f"Layer {layer} is referenced more than once in a `Pad.shapes` entry",
                        hint="Remove the duplicated layer from one of the `Pad.shapes` entries.",
                    )
                other = other_representation(layer)
                if other in layers:
                    raise UserCodeException(
                        f"Layer {layer} and {other} represent the same layer in the {copper_layer_count}-layer board and are both referenced in a `Pad.shapes` entry.",
                        hint=f"Remove either {layer} or {other} from the `Pad.shapes` entries.",
                    )
                layers.add(layer)

    check_layers_exist_in_stackup()
    check_layers_referenced_once()


def translate_pad_shape(pad_shape: Shape | PadShape, into_pad: ppb2.Pad):
    if isinstance(pad_shape, Shape):
        translate_shape(pad_shape, into_pad.shape)
    else:
        translate_shape(pad_shape.shape, into_pad.shape)
        if pad_shape.nfp:
            translate_shape(pad_shape.nfp, into_pad.nfp_shape)


def translate_pad_stack(
    pad_stack: dict[int | tuple[int, ...], Shape | PadShape], into_pad: ppb2.Pad
):
    for key, pad_shape in pad_stack.items():
        into_pad_shape = into_pad.shapes.add()
        if isinstance(key, tuple):
            for layer in key:
                translate_layer_index(layer, into_pad_shape.layers.add())
        else:
            translate_layer_index(key, into_pad_shape.layers.add())
        if isinstance(pad_shape, Shape):
            translate_shape(pad_shape, into_pad_shape.shape)
        else:
            translate_shape(pad_shape.shape, into_pad_shape.shape)
            if pad_shape.nfp:
                translate_shape(pad_shape.nfp, into_pad_shape.nfp)


def translate_model3d(model: Model3D, into_lp: lpb2.Landpattern):
    into_model = into_lp.model3ds.add()
    into_model.filename = model.filename
    position = into_model.position
    scale = into_model.scale
    rotation = into_model.rotation
    position.x, position.y, position.z = model.position
    scale.x, scale.y, scale.z = model.scale
    rotation.x, rotation.y, rotation.z = model.rotation


def translate_partial_landpattern(
    lp: Landpattern,
    root_landpattern: Any,
    into_lp: lpb2.Landpattern,
    into_design: dpb2.DesignV1,
    lp_trace: Trace,
    comp_path: RefPath | None,
):
    lp_path = lp_trace.path
    with dispatch(
        lp,
        base_path=Trace(
            lp_trace.path, (lp_trace.transform or IDENTITY) * (lp.transform or IDENTITY)
        ),
    ) as d:

        @d.register
        def _(pad: Pad, trace: Trace):
            idmap.set_parent(pad, root_landpattern, trace)
            pbpad = into_lp.pads.add()
            pbpad.id = mapped(id(pad))
            pbpad.ref = pathstring(
                relativeref(trace.path, comp_path if comp_path else lp_path)
            )
            try:
                place, *extra = decompose(pad, Placement)
            except ValueError:
                raise Exception(
                    f"Landpattern {pathstring(lp_path)} contains a pad {pathstring(fieldref(trace.path))} without a placement. Did you forget .at()?"
                ) from None
            if extra:
                raise Exception(
                    f"Landpattern {pathstring(lp_path)} contains a pad {pathstring(fieldref(trace.path))} with more than one placement."
                ) from None
            pbpad.pad = translate_pad(pad, into_design, trace.path)
            pbpad.side = translate_side(place.side)
            if trace.transform:
                place = trace.transform * place
            translate_pose(place, pbpad.pose)

        @d.register
        def _(subpattern: Landpattern, trace: Trace):
            translate_partial_landpattern(
                subpattern, root_landpattern, into_lp, into_design, trace, comp_path
            )

        @d.register
        def _(feature: Feature, trace: Trace):
            translate_feature(feature, into_lp.layers.add, trace.transform)

        @d.register
        def _(model: Model3D, trace: Trace):
            translate_model3d(model, into_lp)


@memoizer
def translate_landpattern(
    lp: Landpattern,
    into_design: dpb2.DesignV1,
    lp_trace: Trace,
    comp_path: RefPath | None,
):
    into_lp = into_design.landpatterns.add()
    into_lp.name = Proxy.type(lp).__name__

    translate_partial_landpattern(lp, lp, into_lp, into_design, lp_trace, comp_path)
    translate_file_info(into_lp.info, lp)

    lp_id = idmap.unique()
    into_lp.id = lp_id
    return lp_id
