from jitx.net import Port
from jitx.copper import Copper
from jitx._structural import pathstring, relativeref, Proxy, RefPath
from jitx.via import Via
from .idmap import idmap, memoizer
from .dispatch import dispatch, Trace

import jitxcore._proto.ports_pb2 as ppb2
import jitxcore._proto.design_pb2 as dpb2


@memoizer
def translate_bundle(port: Port, into_design: dpb2.DesignV1):
    pbbundle = into_design.bundles.add()
    pbbundle.id = idmap.unique()
    pbbundle.name = Proxy.type(port).__name__
    with dispatch(port) as d:

        @d.register
        def _(subport: Port, trace: Trace):
            idmap.set_parent(subport, port, trace)
            pbsubport = pbbundle.ports.add()
            pbsubport.name = pathstring(relativeref(trace.path, RefPath()))
            pbsubport.id = idmap(id(subport))
            if Proxy.type(subport) is Port:
                pbsubport.type.single.SetInParent()
            else:
                pbsubport.type.bundle.bundle = translate_bundle(subport, into_design)

    return pbbundle.id


def translate_port_type(
    port: Port | Copper | Via, into_port_type: ppb2.PortType, into_design: dpb2.DesignV1
):
    if Proxy.type(port) is Port or isinstance(port, Copper) or isinstance(port, Via):
        into_port_type.single.SetInParent()
    else:
        into_port_type.bundle.bundle = translate_bundle(port, into_design)
