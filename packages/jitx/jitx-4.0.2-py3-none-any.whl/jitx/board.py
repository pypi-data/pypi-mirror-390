"""
Board definition
================

This module provides the Board class for defining the physical board shape and signal area.
"""

from ._structural import Structural
from .shapes import Shape


class Board(Structural):
    """Board shape and geometric constraints. Can be subclassed to create a
    template with appropriate shape(s) that may include added mounting holes and
    other geometric elements.

    >>> class MyBoard(Board):
    ...     # 50mm x 30mm board outline
    ...     shape = rectangle(50.0, 30.0)
    ...     signal_area = rectangle(46.0, 26.0)
    """

    shape: Shape
    """The board outline shape."""
    signal_area: Shape | None = None
    """Shape constraining component and routing placement area. If not provided, the board shape is used."""
