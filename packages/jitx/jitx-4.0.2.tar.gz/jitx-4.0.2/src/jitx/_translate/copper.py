from jitx.copper import Copper, Pour

from jitx._translate.layerindex import translate_layer_index
from jitx._translate.shape import translate_shape

import jitxcore._proto.geom_pb2 as gpb2


def translate_copper(c: Copper, into_geom: gpb2.Geom):
    if isinstance(c, Pour):
        into_pour = into_geom.pour
        translate_layer_index(c.layer, into_pour.layer)
        translate_shape(c.shape, into_pour.shape)
        into_pour.isolate = c.isolate
        into_pour.rank = c.rank
        into_pour.orphans = c.orphans
    else:
        into_copper = into_geom.copper
        translate_layer_index(c.layer, into_copper.layer)
        translate_shape(c.shape, into_copper.shape)
