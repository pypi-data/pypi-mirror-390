"""
Anchor positioning system for shapes and schematic elements
===========================================================

This module provides anchors, which are used for positioning shapes and schematic elements.
Anchors represent the 9 cardinal positions (corners, edges, and center) of a bounding box.
"""

from enum import Enum


class Anchor(Enum):
    """Enumeration representing anchor positions for shapes and schematic elements.

    Anchors define reference points for positioning elements relative to their
    bounding boxes. The naming follows compass directions:
    N (North/Top), S (South/Bottom), E (East/Right), W (West/Left), C (Center).

    >>> # Create a rectangle anchored at its top-left corner
    >>> rect = rectangle(10, 5, anchor=Anchor.NW)
    >>> # Create a rectangle centered at the origin
    >>> rect = rectangle(10, 5, anchor=Anchor.C)
    """

    NW = "NW"
    N = "N"
    NE = "NE"
    W = "W"
    C = "C"
    E = "E"
    SW = "SW"
    S = "S"
    SE = "SE"

    def horizontal(self):
        """Extract the horizontal component of an Anchor.

        Returns:
            Anchor: The horizontal component (W, C, or E).

        >>> Anchor.NW.horizontal()
        <Anchor.W: 'W'>
        """
        if self in [Anchor.NW, Anchor.W, Anchor.SW]:
            return Anchor.W
        elif self in [Anchor.NE, Anchor.E, Anchor.SE]:
            return Anchor.E
        else:
            return Anchor.C

    def vertical(self):
        """Extract the vertical component of an Anchor.

        Returns:
            Anchor: The vertical component (N, C, or S).

        >>> Anchor.NW.vertical()
        <Anchor.N: 'N'>
        """
        if self in [Anchor.NW, Anchor.N, Anchor.NE]:
            return Anchor.N
        elif self in [Anchor.SW, Anchor.S, Anchor.SE]:
            return Anchor.S
        else:
            return Anchor.C

    def flip(self):
        """Flip the anchor about both X and Y axes.

        Returns:
            Anchor: The diagonally opposite anchor position.

        >>> Anchor.NW.flip()
        <Anchor.SE: 'SE'>
        """
        match self:
            case Anchor.NW:
                return Anchor.SE
            case Anchor.N:
                return Anchor.S
            case Anchor.NE:
                return Anchor.SW
            case Anchor.W:
                return Anchor.E
            case Anchor.C:
                return Anchor.C
            case Anchor.E:
                return Anchor.W
            case Anchor.SW:
                return Anchor.NE
            case Anchor.S:
                return Anchor.N
            case Anchor.SE:
                return Anchor.NW

    def to_point(
        self, bounds: tuple[float, float, float, float]
    ) -> tuple[float, float]:
        """Convert an anchor to a point within the given bounding box.

        Args:
            bounds: Bounding box as (min_x, min_y, max_x, max_y).

        Returns:
            The (x, y) coordinates of the anchor position within the bounds.

        >>> bounds = (0, 0, 10, 5)
        >>> Anchor.NW.to_point(bounds)
        (0, 5)
        >>> Anchor.C.to_point(bounds)
        (0.0, 0.0)
        """
        lox, loy, hix, hiy = bounds
        match self.horizontal():
            case Anchor.W:
                x = lox
            case Anchor.C:
                x = 0.0
            case Anchor.E:
                x = hix
        match self.vertical():
            case Anchor.N:
                y = hiy
            case Anchor.C:
                y = 0.0
            case Anchor.S:
                y = loy
        return (x, y)
