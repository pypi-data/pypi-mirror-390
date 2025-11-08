"""
Schematic generation and templates
==================================

This module provides classes for schematic templates, author tables,
title pages, and schematic markings.
"""

from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass
from jitx.anchor import Anchor

from jitx._structural import Structural, Critical


class SchematicTemplate(Structural):
    """Template for schematic author table.

    >>> class MySchematicTemplate(SchematicTemplate):
    ...     width = 108
    ...     height = 32
    ...     table = AuthorTable(
    ...         rows=[
    ...             AuthorRow(
    ...                 cells=[
    ...                     DataCell(value=">TITLE", width=0.7),
    ...                     TableCell(
    ...                         table=AuthorTable(
    ...                             rows=[
    ...                                 AuthorRow(cells=[DataCell(value="JITX Inc.")]),
    ...                                 AuthorRow(
    ...                                     cells=[DataCell(value="sheet >SHEET/>NUMSHEETS")],
    ...                                     height=0.3,
    ...                                 ),
    ...                             ]
    ...                         ),
    ...                     ),
    ...                 ],
    ...             ),
    ...             AuthorRow(
    ...                 cells=[DataCell(value="May 18, 2026")],
    ...                 height=0.2,
    ...             ),
    ...         ]
    ...     )
    """

    name: str | None = None
    """Optional name for the template."""
    table: AuthorTable
    """Author table for the schematic."""
    width: int
    """Width of the schematic page, in grid units."""
    height: int
    """Height of the schematic page, in grid units."""


@dataclass
class AuthorTable(Critical):
    """Table containing author information on schematics."""

    rows: Sequence[AuthorRow]
    """Rows in the author table."""


@dataclass
class AuthorRow(Critical):
    """Row in an author table."""

    cells: Sequence[AuthorCell]
    """Cells in this row."""
    height: float | None = None
    """
    Optional height of the row, expressed as a percentage of the total table height.
    A row with `height=0.7` will be 70% the height of the table.
    """


@dataclass
class AuthorCell(Critical):
    """Base class for cells in an author table."""

    pass


@dataclass
class DataCell(AuthorCell):
    """Cell containing text data."""

    value: str
    """Text content of the cell."""
    width: float | None = None
    """Optional width of the cell, expressed as a fraction of the total table width.
    A cell with `width=0.7` will be 70% the width of the table.
    """


@dataclass
class TableCell(AuthorCell):
    """Cell containing a nested table."""

    table: AuthorTable
    """Nested table within this cell."""
    width: float | None = None
    """Optional width of the cell, expressed as a fraction of the total table width.
    A cell with `width=0.7` will be 70% the width of the table.
    """


@dataclass
class SchematicTitlePage:
    """A title page for a schematic.

    >>> class MyDesign(Design):
    ...     schematic_title_page = SchematicTitlePage(
    ...         \"\"\"<svg width="279" height="216" viewBox="0 0 279 216" xmlns="http://www.w3.org/2000/svg">
    ...                    <defs>
    ...                        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
    ...                            <stop offset="0%" stop-color="#667EEA" />
    ...                            <stop offset="100%" stop-color="#764BA2" />
    ...                        </linearGradient>
    ...                    </defs>
    ...                    <rect x="0" y="0" width="279" height="216" rx="12" fill="url(#bgGradient)" />
    ...                    <text x="139" y="120" font-family="Arial, Helvetica, sans-serif" font-size="36" fill="white" font-weight="bold" text-anchor="middle">Title Page</text>
    ...               </svg>\"\"\",
    ...     )
    """

    title: str
    """Title page SVG or group."""


class SchematicMarking:
    """A marking on a schematic page.

    >>> class MyDesign(Design):
    ...     schematic_markings = [
    ...         SchematicMarking(
    ...             '<g><text x="-55" y="0" font-family="Arial" font-size="20" fill="black">Hello, world!</text></g>',
    ...             Anchor.S,
    ...         ),
    ...     ]
    """

    marking: str
    """Marking SVG or group."""
    anchor: Anchor
    """Anchor position for the marking."""

    def __init__(self, marking: str, anchor: Anchor = Anchor.SW):
        """Initialize a schematic marking.

        Args:
            marking: Marking SVG or group.
            anchor: Anchor position for the marking. Defaults to SW.
        """
        self.marking = marking
        self.anchor = anchor
