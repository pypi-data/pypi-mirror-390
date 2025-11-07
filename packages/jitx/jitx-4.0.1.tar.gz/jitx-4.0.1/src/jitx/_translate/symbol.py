from jitx._translate.fileinfo import translate_file_info
from jitx.compat.altium import AltiumSymbolProperty
from jitx.shapes import Shape
from jitx._structural import RefPath, fieldref, pathstring, relativeref
from jitx import UserCodeException

import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.enums_pb2 as epb2

from jitx.symbol import Direction, Pin, Symbol, SymbolOrientation
from jitx.transform import ImmutableTransform

from .idmap import idmap, memoizer
from .shape import translate_shape
from .dispatch import dispatch, Trace

SCALE = ImmutableTransform.scale(1.27)  # 50 mils / 1.27mm - TODO configurable?


@memoizer
def translate_symbol(symbol: Symbol, into_design: dpb2.DesignV1, symb_path: RefPath):
    into_symb = into_design.symbols.add()
    into_symb.name = type(symbol).__name__
    has_orientation = False
    with dispatch(symbol, base_path=symb_path) as d:

        def translate_symbol_shape(draw: Shape, trace: Trace):
            layer = into_symb.layers.add()
            layer.name = pathstring(fieldref(trace.path))
            if trace.transform:
                translate_shape(SCALE * trace.transform * draw, layer.shape)
            else:
                translate_shape(SCALE * draw, layer.shape)

        def translate_symbol_pin(
            pin: Pin,
            trace: Trace,
            pin_name_size: float | None,
            pad_name_size: float | None,
        ):
            idmap.set_parent(pin, symbol, trace)
            pbpin = into_symb.pins.add()
            pbpin.ref = pathstring(relativeref(trace.path, symb_path))
            pbpin.id = idmap(id(pin))
            if trace.transform:
                if trace.transform._rotate % 90 != 0:
                    raise ValueError(
                        f"Rotation {trace.transform._rotate} applied to symbol {into_symb.name} is not a multiple of 90 degrees"
                    )
                pin_point = trace.transform * pin.at
                pbpin.point.x, pbpin.point.y = SCALE * pin_point

                # Apply rotation to pin direction
                rotation_90_steps = int(trace.transform._rotate // 90) % 4

                # Rotate direction by the number of 90-degree steps
                direction_map = {
                    Direction.Up: [
                        Direction.Up,
                        Direction.Right,
                        Direction.Down,
                        Direction.Left,
                    ],
                    Direction.Right: [
                        Direction.Right,
                        Direction.Down,
                        Direction.Left,
                        Direction.Up,
                    ],
                    Direction.Down: [
                        Direction.Down,
                        Direction.Left,
                        Direction.Up,
                        Direction.Right,
                    ],
                    Direction.Left: [
                        Direction.Left,
                        Direction.Up,
                        Direction.Right,
                        Direction.Down,
                    ],
                }

                rotated_direction = direction_map[pin.direction][rotation_90_steps]

                # Set direction and length based on rotated direction
                if rotated_direction == Direction.Up:
                    pbpin.properties.dir = epb2.UP
                    pbpin.properties.length = (
                        pin.length * SCALE._scale[1] * trace.transform._scale[1]
                    )
                elif rotated_direction == Direction.Down:
                    pbpin.properties.dir = epb2.DOWN
                    pbpin.properties.length = (
                        pin.length * SCALE._scale[1] * trace.transform._scale[1]
                    )
                elif rotated_direction == Direction.Left:
                    pbpin.properties.dir = epb2.LEFT
                    pbpin.properties.length = (
                        pin.length * SCALE._scale[0] * trace.transform._scale[0]
                    )
                elif rotated_direction == Direction.Right:
                    pbpin.properties.dir = epb2.RIGHT
                    pbpin.properties.length = (
                        pin.length * SCALE._scale[0] * trace.transform._scale[0]
                    )
            else:
                pbpin.point.x, pbpin.point.y = SCALE * pin.at

                # Set direction and length when no transform is applied
                if pin.direction == Direction.Up:
                    pbpin.properties.dir = epb2.UP
                    pbpin.properties.length = pin.length * SCALE._scale[1]
                elif pin.direction == Direction.Down:
                    pbpin.properties.dir = epb2.DOWN
                    pbpin.properties.length = pin.length * SCALE._scale[1]
                elif pin.direction == Direction.Left:
                    pbpin.properties.dir = epb2.LEFT
                    pbpin.properties.length = pin.length * SCALE._scale[0]
                elif pin.direction == Direction.Right:
                    pbpin.properties.dir = epb2.RIGHT
                    pbpin.properties.length = pin.length * SCALE._scale[0]

            # Override the symbol's pin_name_size and pad_name_size if the pin has its own
            if pin.pin_name_size is not None:
                pin_name_size = pin.pin_name_size
            if pin.pad_name_size is not None:
                pad_name_size = pin.pad_name_size
            if pin_name_size is not None:
                pbpin.properties.number_size = pin_name_size * SCALE._scale[0]
            if pad_name_size is not None:
                pbpin.properties.name_size = pad_name_size * SCALE._scale[0]

        def translate_symbol_orientation(orientation: SymbolOrientation, path: RefPath):
            nonlocal has_orientation
            if has_orientation:
                raise ValueError(
                    f"Symbol orientation set multiple times in {into_symb.name}"
                )
            into_orient = into_symb.symbol_orientation
            if len(orientation.rotations) == 0:
                into_orient.any_rotation.SetInParent()
            else:
                for r in orientation.rotations:
                    into_orient.prefer_rotation.rotations.append(r // 90)
            has_orientation = True

        def translate_sub_symbol(
            subsymbol: Symbol,
            trace: Trace,
            pin_name_size: float | None,
            pad_name_size: float | None,
        ):
            with dispatch(subsymbol, base_path=trace) as d2:

                @d2.register
                def _(subsubsymbol: Symbol, subtrace: Trace):
                    translate_sub_symbol(
                        subsubsymbol, subtrace, pin_name_size, pad_name_size
                    )

                @d2.register
                def _(draw: Shape, subtrace: Trace):
                    translate_symbol_shape(draw, subtrace)

                @d2.register
                def _(pin: Pin, subtrace: Trace):
                    translate_symbol_pin(pin, subtrace, pin_name_size, pad_name_size)

        @d.register
        def _(subsymbol: Symbol, trace: Trace):
            translate_sub_symbol(
                subsymbol, trace, symbol.pin_name_size, symbol.pad_name_size
            )

        @d.register
        def _(draw: Shape, trace: Trace):
            translate_symbol_shape(draw, trace)

        @d.register
        def _(pin: Pin, trace: Trace):
            translate_symbol_pin(pin, trace, symbol.pin_name_size, symbol.pad_name_size)

        @d.register
        def _(orientation: SymbolOrientation, path: RefPath):
            translate_symbol_orientation(orientation, path)

    if altium_symbol := AltiumSymbolProperty.get(symbol):
        into_symb.altium_substitution = altium_symbol.symbol.value
        # If there is an AltiumSymbol, then the symbol must have exactly one pin at (0, 0).
        if len(into_symb.pins) != 1:
            raise UserCodeException(
                f"{symbol.__module__}.{symbol.__class__.__name__} has an AltiumSymbolProperty and requires exactly one pin at (0, 0), but it has {len(into_symb.pins)} pins"
            )
        if into_symb.pins[0].point.x != 0 or into_symb.pins[0].point.y != 0:
            raise UserCodeException(
                f"{symbol.__module__}.{symbol.__class__.__name__} has an AltiumSymbolProperty and requires exactly one pin at (0, 0), but it has a pin at a different point"
            )

    translate_file_info(into_symb.info, symbol)

    symb_id = idmap.unique()
    into_symb.id = symb_id
    return symb_id
