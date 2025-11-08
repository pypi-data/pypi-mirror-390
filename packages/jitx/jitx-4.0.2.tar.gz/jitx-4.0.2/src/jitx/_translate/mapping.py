from jitx.net import Port
import jitxcore._proto.mapping_pb2 as mpb2

from jitx.circuit import Circuit

from .idmap import idmap


def translate_port_mapping(
    port1: Port, port2: Port, into_mapping: mpb2.IDMappingEntry, circuit: Circuit
):
    idmap.request_local(into_mapping.key, port1, circuit)
    idmap.request_local(into_mapping.value, port2, circuit)
