"""Composite shape generation functions.

This module provides functions for creating common geometric shapes like
rectangles, capsules, triangles, and other composite shapes used in JITX designs.
These functions generate :py:class:`~jitx.shapes.Shape` objects with the specified dimensions and properties.
"""

from __future__ import annotations

import math
from itertools import chain
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, cast
import shapely
from jitx.shapes.primitive import (
    Arc,
    ArcPolygon,
    Circle,
    Polygon,
    ArcPolyline,
    Polyline,
)
from jitx.shapes.shapely import ShapelyGeometry
from jitx.shapes import Shape
from jitx.anchor import Anchor
from jitx.transform import Point, Transform, IDENTITY


if TYPE_CHECKING:
    _APs = list[Arc | Point]


type Bounds = tuple[float, float, float, float]


def compute_rect_anchor_transform(anchor: Anchor, x: float, y: float) -> Transform:
    """Compute transform to position a rectangle according to an anchor.

    Args:
        anchor: Anchor position for the rectangle.
        x: Half-width of the rectangle.
        y: Half-height of the rectangle.

    Returns:
        Transform that positions the rectangle according to the anchor.
    """
    hMap = {
        Anchor.W: Transform.translate((x, 0)),
        Anchor.C: IDENTITY,
        Anchor.E: Transform.translate((-x, 0)),
    }
    vMap = {
        Anchor.N: Transform.translate((0, -y)),
        Anchor.C: IDENTITY,
        Anchor.S: Transform.translate((0, y)),
    }
    defTx = hMap[anchor.horizontal()] * vMap[anchor.vertical()]
    return defTx


def compute_shape_anchor_transform(anchor: Anchor, coreSh: Shape) -> Transform:
    """Compute transform to position a shape according to an anchor.

    Args:
        anchor: Anchor position for the shape.
        coreSh: Shape to compute anchor transform for.

    Returns:
        Transform that positions the shape according to the anchor.
    """
    minX, minY, maxX, maxY = coreSh.to_shapely().bounds
    w = abs(maxX - minX)
    h = abs(maxY - minY)
    return compute_rect_anchor_transform(anchor, x=w / 2, y=h / 2)


def rectangle(
    width: float,
    height: float,
    *,
    radius: float | Bounds | None = None,
    chamfer: float | Bounds | None = None,
    anchor: Anchor = Anchor.C,
) -> Shape[Polygon | ArcPolygon]:
    """Create an axis aligned rectangle at the origin.

    Args:
        width: X-dimension size of the rectangle in mm.
        height: Y-dimension size of the rectangle in mm.
        radius:
            Optional parameter to round the corners of the rectangle. Value in mm
              - If this is a singular float - then that radius is applied to all 4 corners.
              - If this is a tuple of 4 floats - then each float is applied to
                the corners of the rectangle individually, starting with the
                top-right quadrant (+X, +Y) and then moving counter-clockwise.
              - If `None` - then no rounding occurs.
        chamfer:
            Optional parameter to chamfer the corners of the rectangle. Value in mm.
              - If this is a singular float - then that chamfer is applied to all 4 corners.
              - If this is a tuple of 4 floats - then each float is applied to the corners
                of the rectangle individually, starting with the top-right corner (+X, +Y)
                and then moving counter-clockwise.
              - If `None` - then no chamfering occurs.
        anchor: Localizes the rectangle feature around the origin. The default
            value is :py:class:`~jitx.anchor.Anchor.C` which means that the rectangle is centered about the
            origin for both the X and Y axes. If provided the value :py:class:`~jitx.anchor.Anchor.NW`, then
            the rectangle is created such that its top-left corner is located at the origin
            and the rest of the rectangle projects to the right and down.

    Returns:
        A :py:class:`~jitx.shapes.Shape` containing a
        :py:class:`~jitx.shapes.primitive.Polygon` or
        :py:class:`~jitx.shapes.primitive.ArcPolygon` with the characteristics
        described above.

    To create a normal 1x2 rectangle centered around the middle of the
    rectangle, you can do the following:
    >>> shape = rectangle(1.0, 2.0)

    Simliarly to create a 1x2 rectangle with rounded corners:
    >>> shape = rectangle(1.0, 2.0, radius=0.25)

    To create a 1x2 rectangle with chamfered corners:
    >>> shape = rectangle(1.0, 2.0, chamfer=0.25)

    Rounded and chamfered corners can be applied simultaneously to the
    rectangle, causing the corners from the chamfer to be rounded:
    >>> shape = rectangle(1.0, 2.0, radius=0.25, chamfer=0.25)

    Rounded or chamfered corners can be applied individually to each corner of
    the rectangle.
    >>> shape = rectangle(1.0, 2.0, radius=(0.1, 0.2, 0.3, 0.4))

    To create a 1x2 rectangle anchored in the north-west corner, such that the
    rectangle projects to the right and down:
    >>> rectangle(1.0, 2.0, anchor=Anchor.NW)
    """
    w2 = width / 2.0
    h2 = height / 2.0

    def norm(vs: float | Bounds | None):
        if vs is None:
            return (0, 0, 0, 0)
        elif isinstance(vs, tuple):
            return vs
        else:
            return (vs, vs, vs, vs)

    ne, nw, sw, se = (
        c if c else r for r, c in zip(norm(radius), norm(chamfer), strict=True)
    )
    if nw + ne > width or sw + se > width:
        raise ValueError("Corner radii cannot exceed the width of the polygon")
    if nw + sw > height or ne + se > height:
        raise ValueError("Corner radii cannot exceed the height of the polygon")
    arced = False
    cne, cnw, csw, cse = norm(chamfer)
    # fmt: off
    corners: tuple[_APs, _APs, _APs, _APs] = (
        [( w2,        h2 - cne), ( w2 - cne,   h2)]       if cne else [(w2, h2)],
        [(-w2 + cnw,  h2),       (-w2,         h2 - cnw)] if cnw else [(-w2, h2)],
        [(-w2,       -h2 + csw), (-w2 + csw,  -h2)]       if csw else [(-w2, -h2)],
        [( w2 - cse, -h2),       ( w2,        -h2 + cse)] if cse else [(w2, -h2)],
    )
    # fmt: on
    if radius is not None:
        arced = True

        def arc(pts: list[Arc | Point], radius: float, start: float, arc: float):
            if radius <= 0:
                return
            div = arc / len(pts)
            for i, pt in enumerate(pts):
                if isinstance(pt, tuple):
                    s_deg = start + i * div
                    s = math.radians(s_deg)
                    alpha = math.radians(div / 2)
                    r = radius / math.cos(alpha)
                    sx = r * math.cos(s + alpha)
                    sy = r * math.sin(s + alpha)
                    x, y = pt
                    pts[i] = Arc((x - sx, y - sy), radius, s_deg, div)

        for i, r in enumerate(norm(radius)):
            arc(corners[i], r, 90 * i, 90)
    if arced:
        coreSh = ArcPolygon(tuple(chain.from_iterable(corners)))
    else:
        coreSh = Polygon(cast(Sequence[Point], tuple(chain.from_iterable(corners))))
    if anchor is Anchor.C:
        return coreSh
    defTx = compute_rect_anchor_transform(anchor, w2, h2)
    return defTx * coreSh


def rectangle_from_bounds(bounds: Bounds) -> Polygon:
    """Construct a rectangular polygon from a `shapely.bounds` tuple.

    Args:
        bounds: Tuple of 4 values [minx, miny, maxx, maxy]

    Returns:
        Polygon with 4-sides representing the axis-aligned bounding rectangle
        defined by the `bounds` argument.
    """
    minx, miny, maxx, maxy = bounds
    return Polygon(elements=[(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])


def bounds_union(
    boxes: Iterable[Bounds],
) -> Bounds:
    """Combine multiple bounding boxes into a single bounding box.

    Args:
        boxes: Iterable of bounding box tuples (minx, miny, maxx, maxy).

    Returns:
        Combined bounding box containing all input boxes.
    """
    """Combine multiple bounding boxes into a single bounding box"""
    inf = float("inf")
    minx = inf
    miny = inf
    maxx = -inf
    maxy = -inf
    for lox, loy, hix, hiy in boxes:
        minx = min(minx, lox)
        miny = min(miny, loy)
        maxx = max(maxx, hix)
        maxy = max(maxy, hiy)
    return (minx, miny, maxx, maxy)


def buffer_bounds(bounds: Bounds, amount: float | tuple[float, float]) -> Bounds:
    """Expand bounding box by the specified amount.

    Args:
        bounds: Original bounding box (minx, miny, maxx, maxy).
        amount: Buffer amount. If float, applied equally to all sides.
                If tuple, (dx, dy) for horizontal and vertical buffering.

    Returns:
        Expanded bounding box.
    """
    if isinstance(amount, tuple):
        dx, dy = amount
    else:
        dx = amount
        dy = amount
    return (
        bounds[0] - dx,
        bounds[1] - dy,
        bounds[2] + dx,
        bounds[3] + dy,
    )


def bounds_dimensions(bounds: Bounds) -> tuple[float, float]:
    """Get width and height of a bounding box.

    Args:
        bounds: Bounding box (minx, miny, maxx, maxy).

    Returns:
        Tuple of (width, height).
    """
    return (bounds[2] - bounds[0], bounds[3] - bounds[1])


def bounds_area(bounds: Bounds) -> float:
    """Calculate area of a bounding box.

    Args:
        bounds: Bounding box (minx, miny, maxx, maxy).

    Returns:
        Area of the bounding box, or 0 if invalid dimensions.
    """
    width, height = bounds_dimensions(bounds)
    if width <= 0.0 or height <= 0.0:
        return 0.0
    else:
        return width * height


def plus_symbol(
    length: float | tuple[float, float],
    line_width: float | tuple[float, float],
    *,
    anchor: Anchor = Anchor.C,
) -> Shape:
    """Generate a "+" plus symbol shape
    The plus symbol shape is often used for localization markers (ie, origin of a component)
    or used to indicate the positive (anode) terminal of a capacitor.

    Args:
        length:
            If a single float, then this length is applied to both the
            horizontal and vertical bars. If a tuple of 2 floats, then the
            first float is the horizontal bar length and the second is the
            vertical bar length
        line_width:
            If a single float, then this is the width of the line used for the
            horizontal and vertical bars.  If a tuple of 2 floats, then the
            first float is the horizontal bar width and the second is the
            vertical bar width.
        anchor:
            Placement of the plus symbol with respect to the origin. By default
            this value is :py:class:`~jitx.anchor.Anchor.C` implying that the plus sign is located
            with is cross centered at (0,0)

    Returns:
        A polygon shape in the form of a `+` according the passed arguments. This shape will be centered at the origin.
    """
    if isinstance(length, tuple):
        hl, vl = length
    else:
        hl, vl = (length, length)

    if isinstance(line_width, tuple):
        hw, vw = line_width
    else:
        hw, vw = (line_width, line_width)

    hl2 = hl / 2
    hbar = shapely.LineString([(-hl2, 0), (hl2, 0)]).buffer(hw / 2)
    vl2 = vl / 2
    vbar = shapely.LineString([(0, -vl2), (0, vl2)]).buffer(vw / 2)

    coreSh = ShapelyGeometry(shapely.unary_union([hbar, vbar]))
    defTx = compute_shape_anchor_transform(anchor, coreSh)
    return defTx * coreSh.to_primitive()


def capsule(
    width: float,
    height: float,
    *,
    anchor: Anchor = Anchor.C,
) -> Shape[Circle] | Shape[Polyline]:
    """Create a capsule shape represented by a line with a thickness.
    Fillets the end of the shorter side (min(width,height)) with a radius of half that sides dimension.
    So if `width < height` - then the length of the capsule is in the Y dimension.
    If `width > height` - then the length of the capsule is in the X dimension.
    If `width == height` - then a circle is returned.

    Args:
        width: X dimension of the constructed capsule shape.
        height: Y dimension of the constructed capsule shape.
        anchor: Localizes the capsule shape around the origin. The default
            value is :py:class:`~jitx.anchor.Anchor.C` which means that the capsule is centered about
            the origin for both the X and Y axes. If provided the value
            :py:class:`~jitx.anchor.Anchor.NW`, then the capsule is created such that its top edge
            abuts X axis and its left edge abuts the Y axis.
    """
    if width == height:
        return Circle(diameter=width)
    thick = min(width, height)
    w_2 = width / 2
    h_2 = height / 2
    t_2 = thick / 2

    if width > height:
        capL = w_2 - t_2
        if not capL > 0.0:
            # should only happen if capL is NaN.
            raise ValueError("Invalid Capsule Shape?")
        coreSh = Polyline(thick, [(-capL, 0), (capL, 0)])
    else:
        capL = h_2 - t_2
        if not capL > 0.0:
            raise ValueError("Invalid Capsule Shape?")
        coreSh = Polyline(thick, [(0, -capL), (0, capL)])

    if anchor is Anchor.C:
        return coreSh
    defTx = compute_rect_anchor_transform(anchor, w_2, h_2)
    return defTx * coreSh


def equilateral_triangle(
    side: float,
    *,
    radius: float | None = None,
    anchor: Anchor = Anchor.C,
):
    """Construct an equilateral triangle from a given side.
    Constructed triangle is drawn with one side (the base)
    drawn parallel to the X axis and in the negative half plane
    of the Y axis. The tip of the triangle is in the positive half
    plane of the Y axis.

    Args:
        side: side length of the equilateral triangle
        radius: Optional corner rounding radius for this shape.
        anchor: Initial anchoring of the triangle. Default is :py:class:`~jitx.anchor.Anchor.C` which
            means that the triangle is centered at (0,0)
    """

    def compute_height(s: float) -> float:
        return math.sqrt(3) * s / 2.0

    def make_triangle(h: float, s: float) -> Polygon:
        h2 = h / 2.0
        s2 = s / 2.0
        return Polygon(elements=[(-s2, -h2), (0.0, h2), (s2, -h2)])

    if radius is not None:
        inscribe_radius = side * math.sqrt(3) / 6.0
        if radius >= inscribe_radius:
            raise ValueError(
                f"Invalid Round Radius - radius < inscribed circle radius: {radius} < {inscribe_radius}"
            )

        rSide = (inscribe_radius - radius) * 6.0 / math.sqrt(3)
        rH = compute_height(rSide)
        sh = make_triangle(rH, rSide)
        coreSh = sh.to_shapely().buffer(radius)
    else:
        h = compute_height(side)
        coreSh = make_triangle(h, side)

    if anchor is Anchor.C:
        return coreSh
    defTx = compute_shape_anchor_transform(anchor, coreSh)
    return defTx * coreSh


def notch_rectangle(
    width: float,
    height: float,
    notch_width: float,
    notch_height: float,
    anchor: Anchor = Anchor.C,
) -> Shape[Polygon]:
    """Construct a rectangular shape with a triangular notch
    on one edge of the rectangle. This shape is often used
    with differential via structures. The notch will be
    taken out of the top edge (+Y) of the rectangle.

    Args:
        width: X dimension for the overall rectangular shape.
        height: Y dimension for the overall rectangular shape.
        notch_width: Width of the base of the triangle that will be
            notched into the overall rectangle shape. This value must be
            less than the overall width of the rectangle.
        notch_height: Height of the triangle that will be notched
            into the overall rectangle shape. This height must be less
            than the total height of the overall rectangle.
        anchor: Initial anchoring of the rectangle shape. Default is :py:class:`~jitx.anchor.Anchor.C` which
            means that the rectangle is centered at the origin (0, 0).
    """
    assert width > 0
    assert height > 0
    assert notch_width > 0
    assert notch_height > 0

    assert notch_width < width
    assert notch_height < height

    w2 = width / 2.0
    h2 = height / 2.0
    nw2 = notch_width / 2.0
    nh = notch_height

    sh = Polygon(
        [
            (w2, h2),
            (w2, -h2),
            (-w2, -h2),
            (-w2, h2),
            (-nw2, h2),  # start notch
            (0.0, h2 - nh),
            (nw2, h2),
        ]
    )
    if anchor is Anchor.C:
        return sh
    defTx = compute_shape_anchor_transform(anchor, sh)
    return defTx * sh


def double_notch_rectangle(
    width: float,
    height: float,
    notch_width: float,
    notch_height: float,
    anchor: Anchor = Anchor.C,
) -> Shape[Polygon]:
    """Construct a rectangular shape with a triangular notch
    on the two long edges of the rectangle. This shape is often used
    with differential via structures. The notch will be
    taken out of the top edge (+Y) and bottom edge (-Y) of the rectangle.

    Args:
        width: X dimension for the overall rectangular shape.
        height: Y dimension for the overall rectangular shape.
        notch_width: Width of the base of the triangle that will be
            notched into the overall rectangle shape. This value must be less
            than the overall `width` of the rectangle.
        notch_height: Height of the triangle that will be notched
            into the overall rectangle shape. This height must be less
            than `height/2`.
        anchor: Initial anchoring of the rectangle shape. Default is :py:class:`~jitx.anchor.Anchor.C` which
            means that the rectangle is centered at the origin (0, 0).
    """
    assert width > 0
    assert height > 0
    assert notch_width > 0
    assert notch_height > 0

    assert notch_width < width
    assert notch_height < height / 2

    w2 = width / 2.0
    h2 = height / 2.0
    nw2 = notch_width / 2.0
    nh = notch_height

    sh = Polygon(
        [
            (w2, h2),  # Right Side
            (w2, -h2),
            (nw2, -h2),  # Start Bottom Notch
            (0.0, -(h2 - nh)),
            (-nw2, -h2),
            (-w2, -h2),  # Left Side
            (-w2, h2),
            (-nw2, h2),  # Start of Top Notch
            (0.0, h2 - nh),
            (nw2, h2),
        ]
    )
    if anchor is Anchor.C:
        return sh
    defTx = compute_shape_anchor_transform(anchor, sh)
    return defTx * sh


def chipped_circle(
    radius: float, edge_dist: float, anchor: Anchor = Anchor.C
) -> Shape[ArcPolygon]:
    """Construct a single-sided Chipped Circle shape.
    This shape is often used when constructing antipads for
    via structures. Imagine a chord is drawn across one side of the
    circle. This function constructs a shape such that the sliver of
    the circle on the other side of the chord is removed. This ends up
    meaning that circle has one side that is flattened.

    Args:
        radius: Radius for the overall circle shape.
        edge_dist: Distance from the center to the chord edge of the circle.
        anchor: Placement of the chipped circle with respect to the origin. By default
            this value is :py:class:`~jitx.anchor.Anchor.C` implying that the shape is located with the center of
            the circle at (0,0)
    """
    assert radius > 0
    assert edge_dist > 0
    assert edge_dist < radius

    start_angle = math.acos(edge_dist / radius)
    total_angle = 2.0 * math.pi - (2.0 * start_angle)

    sh = ArcPolygon(
        [
            Arc(
                (0.0, 0.0), radius, math.degrees(start_angle), math.degrees(total_angle)
            ),
        ]
    )

    defTx = compute_shape_anchor_transform(anchor, sh)
    return defTx * Transform.rotate(90.0) * sh


def double_chipped_circle(
    radius: float, edge_dist: float, anchor: Anchor = Anchor.C
) -> Shape[ArcPolygon]:
    """Construct a double-sided Chipped Circle shape
    This shape is often used when constructing antipads for
    via structures. Similar to the single-sided chipped circle,
    except the chord is drawn on both sides, opposite the center
    of the circle, creating two flat edges.

    Args:
        radius: Radius for the overall circle shape.
        edge_dist: Distance from the center to the chord edge of the circle.
        anchor: Placement of the chipped circle with respect to the origin. By default
            this value is :py:class:`~jitx.anchor.Anchor.C` implying that the shape is located with the center of
            the circle at (0,0)
    """
    assert radius > 0
    assert edge_dist > 0
    assert edge_dist < radius

    start_angle = math.acos(edge_dist / radius)
    total_angle = math.pi - (2.0 * start_angle)

    sh = ArcPolygon(
        [
            Arc(
                (0.0, 0.0), radius, math.degrees(start_angle), math.degrees(total_angle)
            ),
            Arc(
                (0.0, 0.0),
                radius,
                math.degrees(math.pi + start_angle),
                math.degrees(total_angle),
            ),
        ]
    )

    defTx = compute_shape_anchor_transform(anchor, sh)
    return defTx * Transform.rotate(90.0) * sh


def bullseye(
    radii: Sequence[float],
    line_widths: float | Sequence[float],
    *,
    anchor: Anchor = Anchor.C,
) -> Shape:
    """Construct a bullseye shape consisting of concentric circle outlines of
    a given width.

    Args:
        radii: A sequence of radiuses for the rings of the bullseye. Each entry
            in this sequence indicates a unique ring to be drawn.
        line_widths: Either a single line width to apply to all of the circles or
            a sequence of line widths to apply to each circle. If a sequence, the
            length of this sequence must match the length of ``radii``
        anchor: Initial anchoring of the bullseye shape. The default value is
            :py:attr:`~jitx.anchor.Anchor.C` which centers the bullseye over
            the origin.
    """
    if isinstance(line_widths, int | float):
        line_widths = [line_widths] * len(radii)

    assert len(line_widths) == len(radii)
    assert all(w > 0 for w in line_widths)
    assert all(r > 0 for r in radii)
    both = zip(radii, line_widths, strict=True)
    arcs = [ArcPolyline(w, [Arc((0, 0), r, 0, 360.0)]) for r, w in both]
    arcShs = [x.to_shapely().g for x in arcs]
    solid = ShapelyGeometry(shapely.unary_union(arcShs))

    defTx = compute_shape_anchor_transform(anchor, solid)
    return defTx * solid
