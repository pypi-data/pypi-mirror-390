from collections.abc import Sequence
from itertools import count, chain
from typing import TYPE_CHECKING, cast

from jitx import UserCodeException
from jitx._translate.feature import translate_feature
from jitx._translate.signal_models import translate_pin_model
from jitx.component import Component
from jitx.feature import Feature
from jitx.landpattern import Landpattern, PadMapping, Pad
from jitx.model3d import Model3D
from jitx.net import Port, Provide, _NoConnect
from jitx.inspect import visit, extract
from jitx.si import BridgingPinModel, TerminatingPinModel
from jitx.symbol import Pin, Symbol, SymbolMapping
from jitx._structural import (
    RefPath,
    relativeref,
    pathstring,
    traverse_base,
    unknown_refpath,
    Proxy,
)

import jitxcore._proto.design_pb2 as dpb2

from .fileinfo import translate_file_info_from_class
from .idmap import mapped, idmap
from .landpattern import (
    translate_landpattern,
    translate_model3d,
    translate_partial_landpattern,
)
from .symbol import translate_symbol
from .bundle import translate_port_type
from .dispatch import dispatch, Trace

from logging import getLogger, DEBUG

if TYPE_CHECKING:
    from jitx._translate.circuit import RestrictInfo

logger = getLogger(__name__)


def translate_component(
    component: Component,
    into_design: dpb2.DesignV1,
    comp_path: RefPath,
    restrict_info: "RestrictInfo",
):
    # circular dependency
    from .circuit import translate_provide

    into_comp = into_design.components.add()
    into_comp.name = type(component).__name__
    unit_count = count()
    unit_to_pins: list[list[Pin]] = []
    lp_pads: set[Pad] = set()
    has_symbol: list[Symbol] = []
    # pyright thinks this can only be None if not cast, despite the use of non-local assignment
    has_landpattern: list[tuple[Landpattern | Feature | Model3D, Trace]] = []

    sm_queue: list[tuple[RefPath, SymbolMapping]] = []
    pm_queue: list[tuple[RefPath, PadMapping]] = []

    sym_mapping: dict[Pin, Port] = {}
    lp_mapping: dict[Pad, Port] = {}
    port_sym_mapping: dict[Port, Pin] = {}
    port_lp_mapping: dict[Port, Sequence[Pad]] = {}
    ref_map: dict[Pad | Pin | Port, RefPath] = {}
    with dispatch(component, base_path=comp_path) as d:

        @d.register
        def _(port: Port, trace: Trace):
            pbport = into_comp.ports.add()
            pbport.name = pathstring(relativeref(trace.path, comp_path))
            # TODO this could be a bundle
            pbport.id = mapped(id(port))
            translate_port_type(port, pbport.type, into_design)
            ref_map[port] = trace.path
            for subtrace, subport in visit(port, Port, path=trace.path):
                if subport.is_single_pin():
                    ref_map[subport] = subtrace.path
            idmap.set_parent(port, component, trace)

        @d.register
        def _(nc: _NoConnect, trace: Trace):
            idmap.request_local(into_comp.no_connects.add(), nc.port, component)

        @d.register
        def _(symbol: Symbol, trace: Trace):
            nonlocal has_symbol
            symbol_id = translate_symbol(symbol, into_design, trace.path)
            pbunit = into_comp.symbol_map.units.add()
            pbunit.unit = next(unit_count)
            pbunit.mapping.id = symbol_id
            pin_list: list[Pin] = []
            for pinpath, pin in traverse_base(
                symbol, (Pin,), subclasses=(), path=trace.path
            ):
                pinned = cast(Pin, pin)
                pin_list.append(pinned)
                ref_map[pinned] = cast(RefPath, pinpath)
            unit_to_pins.append(pin_list)
            idmap.set_parent(symbol, component, trace)
            has_symbol.append(symbol)

        @d.register
        def _(lp: Landpattern, trace: Trace):
            nonlocal has_landpattern
            has_landpattern.append((lp, trace))
            for padtrace, pad in visit(lp, Pad, path=trace.path, transform=None):
                lp_pads.add(pad)
                ref_map[pad] = padtrace.path

        @d.register
        def _(ft: Feature, trace: Trace):
            nonlocal has_landpattern
            has_landpattern.append((ft, trace))

        @d.register
        def _(sm: SymbolMapping, trace: Trace):
            sm_queue.append((trace.path, sm))

        @d.register
        def _(pm: PadMapping, trace: Trace):
            pm_queue.append((trace.path, pm))

        @d.register
        def _(p: Provide, trace: Trace):
            translate_provide(
                p,
                into_comp.supports.add(),
                component,
                into_design,
                trace,
                restrict_info,
            )

        @d.register
        def _(bpm: BridgingPinModel, trace: Trace):
            pm = into_comp.pin_models.add()
            a, b = bpm.ports
            idmap.request_local(pm.a, a, component)
            idmap.request_local(pm.b, b, component)
            translate_pin_model(bpm, pm.pin_model)

        @d.register
        def _(tpm: TerminatingPinModel, trace: Trace):
            pm = into_comp.pin_models.add()
            idmap.request_local(pm.a, tpm.port, component)
            translate_pin_model(tpm, pm.pin_model)

    if not has_landpattern:
        raise UserCodeException(
            f"{component.__module__}.{component.__class__.__name__} does not have a landpattern",
            hint=f"Define a landpattern by subclassing jitx.Landpattern and assign an instance of it to {component.__class__.__name__}.",
        )

    if not has_symbol:
        raise UserCodeException(
            f"{component.__module__}.{component.__class__.__name__} does not have a symbol",
            hint="Make sure there's a symbol attached to the component, such as the BoxSymbol from the jitx standard library.",
        )

    root_landpattern = None
    if len(has_landpattern) == 1:
        # if there is one landpattern, use as-is, allow memoization
        lp, trace = has_landpattern[0]
        lp_id = translate_landpattern(lp, into_design, trace, None)
        into_comp.landpattern_map.id = lp_id
        root_landpattern = lp
        idmap.set_parent(root_landpattern, component, trace)
    else:
        # if there are multiple landpatterns, merge them into one
        into_lp = into_design.landpatterns.add()
        into_lp.name = Proxy.type(component).__name__ + " Composite Landpattern"
        root_landpattern = object()
        into_comp.landpattern_map.id = into_lp.id = idmap(id(root_landpattern))
        for lp, trace in has_landpattern:
            if isinstance(lp, Landpattern):
                translate_partial_landpattern(
                    lp, root_landpattern, into_lp, into_design, trace, comp_path
                )
            elif isinstance(lp, Feature):
                translate_feature(lp, into_lp.layers.add, trace.transform)
            elif isinstance(lp, Model3D):
                translate_model3d(lp, into_lp)
            # caution, setting this relation will trick the
            # proxy-stepping-through-container logic and generate a
            # spurious step in the request_local chain
            # idmap.set_parent(lp, root_landpattern)
        idmap.set_parent(root_landpattern, component, None)

    if not sm_queue and has_symbol:
        # attempt default mapping
        # note that entries will be popped from this mapping when iterating over the queue
        sym_mapping = dict(
            zip(
                chain.from_iterable(extract(sym, Pin) for sym in has_symbol),
                (port for port in extract(component, Port) if port.is_single_pin()),
                strict=False,
            )
        )
        port_sym_mapping = {port: pin for pin, port in sym_mapping.items()}

    for path, sm in sm_queue:
        for port, pin in sm.items():
            if pin in sym_mapping and port is not sym_mapping[pin]:
                pinref = ref_map.get(pin, unknown_refpath)
                portref = ref_map.get(port, unknown_refpath)
                otherportref = ref_map.get(sym_mapping[pin], unknown_refpath)
                raise UserCodeException(
                    f"{component.__module__}.{component.__class__.__name__}'s symbol mapping {pathstring(relativeref(path, comp_path))} maps pin {pathstring(relativeref(pinref, comp_path))} to {pathstring(relativeref(otherportref, comp_path))}, which is already mapped to {pathstring(relativeref(portref, comp_path))}"
                )

            if port in port_sym_mapping:
                raise UserCodeException(
                    f"{component.__module__}.{component.__class__.__name__}'s port {pathstring(relativeref(ref_map[port], comp_path))} is mapped multiple times to symbol pins in symbol mapping {pathstring(relativeref(path, comp_path))}"
                )
            sym_mapping[pin] = port
            port_sym_mapping[port] = pin

    if not pm_queue and has_landpattern:
        # attempt default mapping
        lp_mapping = dict(
            zip(
                chain.from_iterable(extract(lp, Pad) for lp, _ in has_landpattern),
                (port for port in extract(component, Port) if port.is_single_pin()),
                strict=False,
            )
        )
        port_lp_mapping = {port: [pad] for pad, port in lp_mapping.items()}

    for path, pm in pm_queue:
        for port, pads in pm.items():
            if isinstance(pads, Pad):
                pads = (pads,)
            for pad in pads:
                if pad in lp_mapping and port is not lp_mapping[pad]:
                    padref = ref_map.get(pad, unknown_refpath)
                    portref = ref_map.get(port, unknown_refpath)
                    otherportref = ref_map.get(lp_mapping[pad], unknown_refpath)
                    raise UserCodeException(
                        f"{component.__module__}.{component.__class__.__name__}'s pad mapping {pathstring(relativeref(path, comp_path))} maps pad {pathstring(relativeref(padref, comp_path))} to {pathstring(relativeref(portref, comp_path))}, which is already mapped to {pathstring(relativeref(otherportref, comp_path))}"
                    )
                lp_mapping[pad] = port
            if port in port_lp_mapping:
                raise UserCodeException(
                    f"{component.__module__}.{component.__class__.__name__}'s port {pathstring(relativeref(ref_map[port], comp_path))} is mapped multiple times to pads in pad mapping {pathstring(relativeref(path, comp_path))}"
                )
            port_lp_mapping[port] = pads

    for port in extract(component, Port):
        if port.is_single_pin():
            if port not in port_sym_mapping:
                portref = ref_map.get(port, unknown_refpath)
                raise UserCodeException(
                    f"{component.__module__}.{component.__class__.__name__}'s port {pathstring(relativeref(ref_map[port], comp_path))} is not mapped to a symbol pin"
                )

            if port not in port_lp_mapping:
                portref = ref_map.get(port, unknown_refpath)
                raise UserCodeException(
                    f"{component.__module__}.{component.__class__.__name__}'s port {pathstring(relativeref(ref_map[port], comp_path))} is not mapped to a pad"
                )

    for pbunit, pins, symbol in zip(
        into_comp.symbol_map.units, unit_to_pins, has_symbol, strict=True
    ):
        for pin in pins:
            port = sym_mapping.pop(pin, None)
            if port is None:
                # Not an issue in the backend to have extraneous pins in the symbol definition
                pinref = ref_map.get(pin, unknown_refpath)
                logger.debug(
                    f"Missing symbol pin mapping of pin {pathstring(relativeref(pinref, comp_path))} in component {pathstring(comp_path)}"
                )
                continue
            entry = pbunit.mapping.entries.add()
            idmap.request_local(entry.key, port, component)
            entry.value.path.append(pbunit.mapping.id)
            idmap.request_local(entry.value, pin, symbol)

    # all entries should have been popped from the mapping by now
    if sym_mapping:
        for pin, port in sym_mapping.items():
            pinref = ref_map.get(pin, unknown_refpath)
            portref = ref_map.get(port, unknown_refpath)
            raise UserCodeException(
                f"{component.__module__}.{component.__class__.__name__}'s symbol mapping has extraneous mapping {pathstring(relativeref(portref, comp_path))} to {pathstring(relativeref(pinref, comp_path))}"
            )

    for pp, port in lp_mapping.items():
        entry = into_comp.landpattern_map.entries.add()
        idmap.request_local(entry.key, port, component)
        entry.value.path.append(into_comp.landpattern_map.id)
        idmap.request_local(entry.value, pp, root_landpattern)
        lp_pads.discard(pp)

    if lp_pads and logger.isEnabledFor(DEBUG):
        pad = lp_pads.pop()
        padref = ref_map.get(pad, unknown_refpath)
        logger.debug(
            f"{component.__module__}.{component.__class__.__name__} is missing a landpattern mapping for {len(lp_pads)} pads, including {pathstring(relativeref(padref, comp_path))}"
        )

    # String Fields
    if component.value is not None:
        val = component.value
        if isinstance(val, str):
            into_comp.value = val
        else:
            into_comp.value = f"{val:g~P}"
    if component.mpn is not None:
        into_comp.mpn = component.mpn
    if component.manufacturer is not None:
        into_comp.manufacturer = component.manufacturer
    if component.reference_designator_prefix is not None:
        into_comp.reference_prefix = component.reference_designator_prefix

    ### String Fields ###
    # Datasheet

    ### Misc Fields ###
    # Spice
    # Pin Models
    # Differential Pairs

    ### File Info ###
    translate_file_info_from_class(into_comp.info, component)

    comp_id = idmap.unique()
    into_comp.id = comp_id
    return comp_id
