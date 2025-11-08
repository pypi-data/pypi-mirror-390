from jitxcore._proto.enums_pb2 import Side
from jitxcore._proto.layers_pb2 import LayerIndex


def translate_layer_index(index: int, into_layer: LayerIndex):
    if index < 0:
        into_layer.index = -index - 1
        into_layer.side = Side.BOTTOM
    else:
        into_layer.index = index
        into_layer.side = Side.TOP
