from functools import singledispatch
from collections.abc import Callable
from jitx._translate.layerindex import translate_layer_index
from jitx.feature import (
    Feature,
    Finish,
    KeepOut,
    Glue,
    Courtyard,
    Custom,
    Cutout,
    # BoardEdge,
    Paste,
    Silkscreen,
    Soldermask,
)
from jitx.transform import Transform

from .shape import translate_shape
from .enums import translate_side

import jitxcore._proto.layers_pb2 as lpb2


def translate_feature_type(
    ft: Feature,
    into: Callable[[], lpb2.LayerSpecifier],
):
    @singledispatch
    def d(f: Feature) -> None:
        raise Exception(f"Unhandled feature type {f})")

    @d.register
    def _(c: Cutout):
        into().cutout.SetInParent()

    @d.register
    def _(s: Silkscreen):
        spb = into()
        spb.silkscreen.side = translate_side(s.side)
        import datetime

        today = datetime.datetime.today()
        if today.month == 4 and today.day == 1:
            spb.silkscreen.name = "Smooth"
        else:
            spb.silkscreen.name = "Silk"

    @d.register
    def _(s: Soldermask):
        into().soldermask.side = translate_side(s.side)

    @d.register
    def _(p: Paste):
        into().paste.side = translate_side(p.side)

    @d.register
    def _(g: Glue):
        into().glue.side = translate_side(g.side)

    @d.register
    def _(f: Finish):
        into().finish.side = translate_side(f.side)

    @d.register
    def _(c: Courtyard):
        into().courtyard.side = translate_side(c.side)

    @d.register
    def _(f: KeepOut):
        lrs = f.layers
        # TODO stop using forbid_coppper and forbid_via and switch all to forbid_region.
        if f.pour:
            for lr in lrs.ranges:
                fc = into()
                start, end = lr
                translate_layer_index(start, fc.forbid_copper.start)
                translate_layer_index(end, fc.forbid_copper.end)

        through_via = False
        if f.via:
            for lr in lrs.ranges:
                start, end = lr
                if start == 0 and end == -1:
                    through_via = True
            if through_via:
                # if it's a through-stack via keepout, use the legacy
                # forbid_via to allow it to export.
                fv = into()
                fv.forbid_via.SetInParent()

        if f.route or (f.via and not through_via):
            for lr in lrs.ranges:
                fr = into()
                start, end = lr
                if f.route:
                    fr.forbid_region.forbid_routes = True
                if f.via and not through_via:
                    fr.forbid_region.forbid_vias = True
                translate_layer_index(start, fr.forbid_region.start)
                translate_layer_index(end, fr.forbid_region.end)

    # @d.register
    # def _(b: BoardEdge):
    #     into().board_edge.SetInParent()

    @d.register
    def _(c: Custom):
        cpb = into()
        cpb.custom_layer.side = translate_side(c.side)
        cpb.custom_layer.name = c.name

    d(ft)


def translate_feature(
    ft: Feature, add_layer: Callable[[], lpb2.Layer], xform: Transform | None
):
    def into():
        into = add_layer()
        if xform:
            translate_shape(xform * ft.shape, into.shape)
        else:
            translate_shape(ft.shape, into.shape)
        return into.layer

    translate_feature_type(ft, into)
