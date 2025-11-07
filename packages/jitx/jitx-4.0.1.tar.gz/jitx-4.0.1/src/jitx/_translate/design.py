from jitx._translate.enums import translate_paper
from jitx._translate.rules import translate_design_rule
from jitx._translate.schematic import translate_schematic_marking
from jitx.board import Board
from jitx.circuit import Circuit
from jitx.context import Context
from jitx.design import Design, name
from jitx._structural import RefPath, pathstring
from jitx.inspect import visit
from jitx.paper import Paper
from jitx.constraints import DesignConstraint
from jitx.schematic import SchematicMarking, SchematicTitlePage, SchematicTemplate
from jitx.substrate import Substrate

import jitxcore._proto.design_pb2 as dpb2
import jitxcore.version as version

from .idmap import idmapper, idmap
from .circuit import InstanceStatus, RestrictInfo, translate_circuit
from .board import translate_board_and_substrate
from .dispatch import dispatch, Trace
from .schematic import translate_schematic_template, translate_schematic_title_page


def package_design(design: Design):
    with idmapper():
        package = dpb2.Design()
        translate_design(design, package.v1)
        idmap.finalize()
        return package


class DesignTranslationContext(Context):
    def __init__(self, design: Design):
        self.design = design


def translate_design(design: Design, root: dpb2.DesignV1):
    boards: list[tuple[RefPath, Board]] = []
    substrates: list[tuple[RefPath, Substrate]] = []
    schematic_templates: list[tuple[RefPath, SchematicTemplate]] = []
    schematic_title_pages: list[tuple[RefPath, SchematicTitlePage]] = []
    circuits: list[tuple[RefPath, Circuit]] = []
    papers: list[tuple[RefPath, Paper]] = []

    root.name = name(design)

    # Ensure that the design has a board, substrate, and circuit in its designated fields.
    # The dispatch will also find these fields -- so if exactly one is found, it will be the contents of the field.
    try:
        board = design.board
        if not isinstance(board, Board):
            raise Exception(f"Design {name(design)}.board is not a Board")
    except AttributeError as err:
        raise Exception(f"Design {name(design)}.board is not defined") from err
    try:
        substrate = design.substrate
        if not isinstance(substrate, Substrate):
            raise Exception(f"Design {name(design)}.substrate is not a Substrate")
    except AttributeError as err:
        raise Exception(f"Design {name(design)}.substrate is not defined") from err
    try:
        circuit = design.circuit
        if not isinstance(circuit, Circuit):
            raise Exception(f"Design {name(design)}.circuit is not a Circuit")
    except AttributeError as err:
        raise Exception(f"Design {name(design)}.circuit is not defined") from err

    with dispatch(design) as d:

        @d.register
        def _(board: Board, trace: Trace):
            if boards:
                boards.append((trace.path, board))
                raise Exception(
                    f"Multiple boards encountered at: {', '.join(pathstring(p) for p, _ in boards)}"
                )
            boards.append((trace.path, board))

        @d.register
        def _(substrate: Substrate, trace: Trace):
            if substrates:
                substrates.append((trace.path, substrate))
                raise Exception(
                    f"Multiple substrates encountered at: {', '.join(pathstring(p) for p, _ in substrates)}"
                )
            substrates.append((trace.path, substrate))

        @d.register
        def _(circuit: Circuit, trace: Trace):
            if circuits:
                circuits.append((trace.path, circuit))
                raise Exception(
                    f"Multiple top-level circuits encountered at: {', '.join(pathstring(p) for p, _ in circuits)}"
                )
            circuits.append((trace.path, circuit))

        @d.register
        def _(schematic_template: SchematicTemplate, trace: Trace):
            if schematic_templates:
                schematic_templates.append((trace.path, schematic_template))
                raise Exception(
                    f"Multiple schematic templates encountered at: {', '.join(pathstring(p) for p, _ in schematic_templates)}"
                )
            schematic_templates.append((trace.path, schematic_template))

        @d.register
        def _(schematic_marking: SchematicMarking, _trace: Trace):
            translate_schematic_marking(schematic_marking, root)

        @d.register
        def _(schematic_title_page: SchematicTitlePage, trace: Trace):
            if schematic_title_pages:
                schematic_title_pages.append((trace.path, schematic_title_page))
                raise Exception(
                    f"Multiple schematic title pages encountered at: {', '.join(pathstring(p) for p, _ in schematic_title_pages)}"
                )
            schematic_title_pages.append((trace.path, schematic_title_page))

        @d.register
        def _(paper: Paper, trace: Trace):
            if papers:
                papers.append((trace.path, paper))
                raise Exception(
                    f"Multiple papers encountered at: {', '.join(pathstring(p) for p, _ in papers)}"
                )
            papers.append((trace.path, paper))

    for trace, rule in visit(design, DesignConstraint, transform=None):
        translate_design_rule(rule, root, trace.path)

    translate_board_and_substrate(boards[0], substrates[0], root)
    if schematic_templates:
        translate_schematic_template(schematic_templates, root)
    if schematic_title_pages:
        translate_schematic_title_page(schematic_title_pages, root)
    if papers:
        root.paper = translate_paper(papers[0][1])

    with DesignTranslationContext(design):
        for path, circuit in circuits:
            root.module = translate_circuit(
                circuit,
                root,
                path,
                InstanceStatus(True, True, False),
                RestrictInfo(circuit, root.restricts),
            )

    root.filenames.extend(idmap.filemap.keys())
    root.version = version.VERSION_MARKER
