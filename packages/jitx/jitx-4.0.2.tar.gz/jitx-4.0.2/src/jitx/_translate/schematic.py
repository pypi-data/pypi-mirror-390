from collections.abc import Sequence
from jitx._translate.fileinfo import translate_file_info
from jitx.schematic import (
    SchematicTemplate,
    AuthorTable,
    AuthorRow,
    AuthorCell,
    DataCell,
    SchematicTitlePage,
    TableCell,
)
from jitx._structural import RefPath, pathstring
from jitx._translate.enums import translate_anchor
from jitx.schematic import SchematicMarking

import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.schematic_pb2 as spb2

from .idmap import idmap


def translate_author_cell(cell: AuthorCell, into_cell: spb2.AuthorCell):
    if isinstance(cell, DataCell):
        into_cell.data.value = cell.value
        if cell.width is not None:
            into_cell.data.width = cell.width
    elif isinstance(cell, TableCell):
        if cell.width is not None:
            into_cell.table.width = cell.width
        translate_author_table(cell.table, into_cell.table.table)


def translate_author_row(row: AuthorRow, into_row: spb2.AuthorRow):
    if row.height is not None:
        into_row.height = row.height
    for cell in row.cells:
        translate_author_cell(cell, into_row.cells.add())


def translate_author_table(table: AuthorTable, into_table: spb2.AuthorTable):
    for row in table.rows:
        translate_author_row(row, into_table.rows.add())


def translate_schematic_template(
    schematic_templates: Sequence[tuple[RefPath, SchematicTemplate]],
    into: dpb2.DesignV1,
) -> None:
    into_template = into.schematic_templates.add()
    has_template = False

    for path, template in schematic_templates:
        if has_template:
            raise Exception(
                f"Design has an extra schematic template at {pathstring(path)}"
            )
        has_template = True

        # Set basic properties
        # FIXME: Board uses mapped(id(board)), check why.
        template_id = idmap.unique()
        into_template.id = template_id

        into.schematic_template = template_id

        if template.name is not None:
            into_template.name = template.name
        else:
            into_template.name = type(template).__name__

        into_template.width = template.width
        into_template.height = template.height

        # Translate the author table
        translate_author_table(template.table, into_template.table)

        translate_file_info(into_template.info, template)


def translate_schematic_title_page(
    schematic_title_pages: Sequence[tuple[RefPath, SchematicTitlePage]],
    into_design: dpb2.DesignV1,
) -> None:
    """Translate a SchematicTitlePage to a protobuf SchematicTitlePage message."""
    has_title_page = False
    for path, title_page in schematic_title_pages:
        if has_title_page:
            raise Exception(
                f"Design has an extra schematic title page at {pathstring(path)}"
            )
        has_title_page = True
        into_design.schematic_title_page = title_page.title


def translate_schematic_marking(
    marking: SchematicMarking,
    into_design: dpb2.DesignV1,
) -> None:
    """Translate a SchematicMarking to a protobuf SchematicPageMarking message."""
    into = into_design.schematic_page_markings.add()
    into.marking = marking.marking
    into.anchor = translate_anchor(marking.anchor)
