from jitx._translate.fileinfo import translate_file_info
from jitx.board import Board
from jitx.error import UserCodeException
from jitx.feature import Cutout, KeepOut, Feature
from jitx.layerindex import LayerSet
from jitx.shapes import Shape
from jitx.shapes.primitive import Polygon, PolygonSet
from jitx.si import DifferentialRoutingStructure, RoutingStructure
from jitx.stackup import Conductor, Dielectric, Material, Stackup
from jitx._structural import RefPath, pathstring
from jitx.substrate import FabricationConstraints, Substrate
from jitx.via import Via

from .feature import translate_feature
from .shape import translate_shape
from .via import translate_via_type
from .idmap import mapped
from .dispatch import dispatch, Trace, warn

import jitxcore._proto.design_pb2 as dpb2

# import jitxcore._proto.stackup_pb2 as spb2
import jitxcore._proto.board_pb2 as bpb2
import jitxcore._proto.enums_pb2 as epb2
import jitxcore._proto.rules_pb2 as rpb2


def translate_stackup(
    stackup: Stackup,
    into_design: dpb2.DesignV1,
    into_board: bpb2.Board,
    path: RefPath,
):
    pbstack = into_design.stackups.add()
    pbstack.id = mapped(id(stackup))
    pbstack.name = stackup.name or type(stackup).__name__
    into_board.stackup = pbstack.id
    materials: set[int] = set()

    translate_file_info(pbstack.info, stackup)

    def add_material(mat: type[Material]):
        if id(mat) not in materials:
            materials.add(id(mat))
            pbmat = into_design.materials.add()
            pbmat.id = mapped(id(mat))
            pbmat.name = mat.name or type(mat).__name__
            translate_file_info(pbmat.info, mat)
            if mat.material_name is not None:
                pbmat.material_name = mat.material_name
            if issubclass(mat, Dielectric):
                pbmat.type = epb2.DIELECTRIC
                if mat.dielectric_coefficient is not None:
                    pbmat.dielectric_coefficient = mat.dielectric_coefficient
                if mat.loss_tangent is not None:
                    pbmat.loss_tangent = mat.loss_tangent
            elif issubclass(mat, Conductor):
                pbmat.type = epb2.CONDUCTOR
                if mat.roughness is not None:
                    pbmat.roughness = mat.roughness
            else:
                raise Exception("Internal error. Invalid material type at:", path)
        return mapped(id(mat))

    with dispatch(stackup, base_path=path) as d:

        @d.register
        def _(layer: Material, trace: Trace):
            pblayer = pbstack.layers.add()
            pblayer.material = add_material(layer.__class__)
            if layer.name is not None:
                pblayer.name = layer.name
            # else:  # Add a flag to enable this somehow?
            #     pblayer.name = pathstring(relativeref(trace.path, path))
            if layer.thickness is None:
                # Shouldn't really happen, but could if someone overrides __init__ and doesn't call super().__init__
                raise UserCodeException(
                    f"Layer {layer.name} has no thickness at {pathstring(trace.path)}.",
                    hint="Add a thickness to the material definition, or set a thickness when creating the layer.",
                )
            pblayer.thickness = layer.thickness


fab_constraints_mapping = {
    "min_copper_width": epb2.ClearanceType.MIN_COPPER_WIDTH,
    "min_copper_copper_space": epb2.ClearanceType.MIN_COPPER_COPPER_SPACE,
    "min_copper_hole_space": epb2.ClearanceType.MIN_COPPER_HOLE_SPACE,
    "min_copper_edge_space": epb2.ClearanceType.MIN_COPPER_EDGE_SPACE,
    "min_annular_ring": epb2.ClearanceType.MIN_ANNULAR_RING,
    "min_drill_diameter": epb2.ClearanceType.MIN_DRILL_DIAMETER,
    "min_silkscreen_width": epb2.ClearanceType.MIN_SILKSCREEN_WIDTH,
    "min_pitch_leaded": epb2.ClearanceType.MIN_PITCH_LEADED,
    "min_pitch_bga": epb2.ClearanceType.MIN_PITCH_BGA,
    "max_board_width": epb2.ClearanceType.MAX_BOARD_WIDTH,
    "max_board_height": epb2.ClearanceType.MAX_BOARD_HEIGHT,
    "min_silk_solder_mask_space": epb2.ClearanceType.MIN_SILK_SOLDER_MASK_SPACE,
    "min_silkscreen_text_height": epb2.ClearanceType.MIN_SILKSCREEN_TEXT_HEIGHT,
    "solder_mask_registration": epb2.ClearanceType.SOLDER_MASK_REGISTRATION,
    "min_soldermask_opening": epb2.ClearanceType.MIN_SOLDER_MASK_OPENING,
    "min_soldermask_bridge": epb2.ClearanceType.MIN_SOLDER_MASK_BRIDGE,
    "min_th_pad_expand_outer": epb2.ClearanceType.MIN_TH_PAD_EXPAND_OUTER,
    "min_hole_to_hole": epb2.ClearanceType.MIN_HOLE_TO_HOLE,
    "min_pth_pin_solder_clearance": epb2.ClearanceType.MIN_PTH_PIN_SOLDER_CLEARANCE,
}


def translate_fab_constraints(
    fab: FabricationConstraints,
    into: rpb2.Rules,
    path: RefPath,
):
    rules_id = mapped(id(fab))
    into.id = rules_id
    into.name = type(fab).__name__
    for constraint in fab_constraints_mapping:
        if not hasattr(fab, constraint):
            raise Exception(f"Missing '{constraint}' constraint at {pathstring(path)}")
        cl = into.clearances.add()
        cl.type = fab_constraints_mapping[constraint]
        cl.value = getattr(fab, constraint)
    return rules_id


def translate_board_and_substrate(
    pathed_board: tuple[RefPath, Board],
    pathed_substrate: tuple[RefPath, Substrate],
    into: dpb2.DesignV1,
):
    # This seems to overwrite fields of one board?
    b1 = into.boards.add()
    path, board = pathed_board
    # FIXME: Don't we just need idmap.unique() here?
    board_id = mapped(id(board))
    b1.id = board_id
    b1.name = type(board).__name__
    into.board = b1.id
    board_shape = board.shape.to_primitive()
    if isinstance(board_shape.geometry, PolygonSet):
        if len(board_shape.geometry.polygons) != 1:
            raise TypeError("A disjoint board shape is currently not support")
        board_shape = Shape(board_shape.geometry.polygons[0], board_shape.transform)
    if isinstance(board_shape.geometry, Polygon):
        holes = board_shape.geometry.holes
        if holes:
            # translate board shape holes to cutouts
            board_shape = Shape(
                Polygon(board_shape.geometry.elements), board_shape.transform
            )
            for hole in holes:
                translate_feature(
                    Cutout(Polygon(tuple(reversed(hole)))),
                    b1.layers.add,
                    board_shape.transform,
                )
    translate_shape(board_shape, b1.boundary)
    if board.signal_area is not None:
        signal_shape = board.signal_area
        if isinstance(signal_shape.geometry, PolygonSet):
            if len(signal_shape.geometry.polygons) != 1:
                raise TypeError("A disjoint signal area shape is currently not support")
            signal_shape = Shape(
                signal_shape.geometry.polygons[0], signal_shape.transform
            )
        if isinstance(signal_shape.geometry, Polygon):
            holes = signal_shape.geometry.holes
            if holes:
                # translate signal area holes to keepouts
                signal_shape = Shape(
                    Polygon(signal_shape.geometry.elements), signal_shape.transform
                )
                for hole in holes:
                    translate_feature(
                        KeepOut(
                            Polygon(tuple(reversed(hole))),
                            LayerSet.all(),
                            pour=True,
                            via=True,
                        ),
                        b1.layers.add,
                        signal_shape.transform,
                    )
        translate_shape(signal_shape, b1.signal_boundary)
    translate_file_info(b1.info, board)
    with dispatch(board) as d:

        @d.register
        def _(ft: Feature, trace: Trace):
            translate_feature(ft, b1.layers.add, trace.transform)

    stackups: list[tuple[RefPath, Stackup]] = []
    constraintss: list[tuple[RefPath, FabricationConstraints]] = []

    path, substrate = pathed_substrate
    try:
        stackup = substrate.stackup
        if not isinstance(stackup, Stackup):
            raise Exception(f"Substrate {pathstring(path)}.stackup is not a Stackup")
    except AttributeError as err:
        raise Exception(f"Substrate {pathstring(path)}.stackup is not defined") from err
    try:
        constraints = substrate.constraints
        if not isinstance(constraints, FabricationConstraints):
            raise Exception(
                f"Substrate {pathstring(path)}.constraints is not a FabricationConstraints"
            )
    except AttributeError as err:
        raise Exception(
            f"Substrate {pathstring(path)}.constraints is not defined"
        ) from err
    with dispatch(substrate, base_path=path) as d:

        @d.register
        def _(typed: type, trace: Trace):
            if issubclass(typed, Via):
                via_id = translate_via_type(typed, into.vias.add())
                b1.vias.append(via_id)
            else:
                warn(
                    f"Unexpected raw type {typed} encountered at {pathstring(trace.path)}"
                )

        @d.register
        def _(structure: RoutingStructure, trace: Trace):
            # ignore, these are used for lookups.
            pass

        @d.register
        def _(structure: DifferentialRoutingStructure, trace: Trace):
            # ignore, these are used for lookups.
            pass

        @d.register
        def _(stackup: Stackup, trace: Trace):
            if stackups:
                stackups.append((trace.path, stackup))
                raise Exception(
                    f"Multiple stackups encountered at: {', '.join(pathstring(p) for p, _ in stackups)}"
                )
            stackups.append((trace.path, stackup))
            translate_stackup(stackup, into, b1, trace.path)

        @d.register
        def _(fab: FabricationConstraints, trace: Trace):
            if constraintss:
                constraintss.append((trace.path, fab))
                raise Exception(
                    f"Multiple constraints encountered at: {', '.join(pathstring(p) for p, _ in constraintss)}"
                )
            constraintss.append((trace.path, fab))
            into.rules = translate_fab_constraints(fab, into.ruless.add(), trace.path)
