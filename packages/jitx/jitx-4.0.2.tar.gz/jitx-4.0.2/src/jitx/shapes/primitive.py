"""
The primitive shape set provides the basis for all shapes in JITX. If a library
is used to create geometry, a :py:class:`~jitx.shapes.ShapeGeometry` interface
should be implemented in order provide a mapping of the library geometry to one
of these primitive shapes. Notably, a shapely ShapeGeometry interface has
already been provided, to seamlessly use the shapely library to generate
geometry for your design.
"""

from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Sequence
from typing import overload

from jitx.anchor import Anchor
from jitx.transform import Point, Vec2D
from . import ShapeGeometry

from math import degrees, sqrt


class Primitive(ShapeGeometry):
    def to_primitive(self) -> Primitive:
        return self


class Empty(Primitive):
    """An empty shape.

    Used to represent the absence of geometry.

    >>> empty = Empty()
    """


class Arc:
    """An Arc is represented using a 2D center point, a radius, a start angle
    between 0 and 360 degrees, and and arc sweep between -360 and 360 where
    positive values indicate counter-clockwise sweep and negative values
    indicate a clockwise sweep.

    Note that arc angles are in degrees, and not in radians, to avoid numerical
    issues with precise 90-degree angles.

    There are two overloaded constructors in addition to the native center, radius,
    start, and sweep. The first takes three points, start, mid, and end, and
    computes the arc from the three points. The second takes a start and end
    point and a radius, and computes the arc from these values.

    >>> # Arc from center, radius, start angle, and sweep
    >>> arc1 = Arc((0, 0), 5, 0, 90)

    >>> # Arc through three points
    >>> arc2 = Arc((0, 0), (1, 1), (2, 0))

    >>> # Arc from start/end points, radius, cw orientation, and whether to draw the larger of two possible arcs.
    >>> arc3 = Arc((0, 0), (10, 0), 5, clockwise=True, large=False)
    """

    center: Point
    """The center coordinates of the arc."""
    radius: float
    """The radius of the arc."""
    start: float
    """The start angle in degrees. Must be between 0 and 360."""
    arc: float
    """The arc sweep angle in degrees. Positive values are counter clockwise.
    Must be between -360 and 360."""

    @overload
    def __init__(self, start: Point, mid: Point, end: Point, /): ...
    @overload
    def __init__(
        self,
        start: Point,
        end: Point,
        radius: float,
        /,
        *,
        clockwise: bool,
        large: bool = False,
    ): ...
    @overload
    def __init__(self, center: Point, radius: float, start: float, arc: float, /): ...

    def __init__(
        self,
        center: Point,
        radius: float | Point,
        start: float | Point,
        arc: float | bool | None = None,
        *,
        clockwise: bool | None = None,
        large: bool | None = None,
    ):
        if isinstance(radius, tuple) and isinstance(start, tuple) and arc is None:
            self.__from_3_points(center, radius, start)
        elif (
            isinstance(radius, tuple)
            and isinstance(start, float | int)
            and arc is None
            and clockwise is not None
        ):
            if large is None:
                large = False
            self.__from_2_points(center, radius, start, cw=clockwise, large=large)
        elif (
            isinstance(center, tuple)
            and isinstance(radius, float | int)
            and isinstance(start, float | int)
            and isinstance(arc, float | int)
        ):
            self.center = center
            self.start = start
            self.radius = radius
            self.arc = arc
        else:
            raise TypeError("Invalid constructor overload used")

        start, arc = self.start, self.arc
        assert 0.0 <= start < 360.0, (
            f"start must be between 0 and 360 degrees, got {start}"
        )
        assert -360.0 <= arc <= 360.0, (
            f"arc must be between -360 and 360 degrees, got {arc}"
        )

    def __repr__(self):
        return f"Arc(center={self.center}, radius={self.radius}, start={self.start}, arc={self.arc})"

    def __set_angles(self, p0: Vec2D, s: Vec2D, e: Vec2D, cw: bool):
        p0s = s - p0
        p0e = e - p0
        self.start = degrees(p0s.angle()) % 360
        diff = (degrees(p0e.angle()) - self.start) % 360
        self.arc = (diff - 360) if cw else diff

    def __from_3_points(self, start: Point, mid: Point, end: Point):
        """Construct an arc from two points and a mid-point."""
        # https://en.wikipedia.org/wiki/Circumcircle
        s = Vec2D(*start)
        m = Vec2D(*mid)
        e = Vec2D(*end)
        a = s - m
        b = e - m
        c = s - e
        a2 = a.dot(a)
        b2 = b.dot(b)
        c2 = c.dot(c)

        axb = a.cross(b)
        adb = a.dot(b)
        if -1e-9 < axb < 1e-9:
            raise ValueError("Points are colinear")
        r = sqrt(a2 * b2 * c2 / (4 * axb**2))

        # fmt: off
        p0 = m + (
            (a2*b2*(a + b) - (adb)*(a2*b + b2*a))
            /
            (2*(a2*b2 - (adb)**2))
        )
        # fmt: on
        self.center = p0.x, p0.y
        self.radius = r
        self.__set_angles(p0, s, e, (axb > 0))

    def __from_2_points(
        self,
        start: Point,
        end: Point,
        r: float,
        *,
        cw: bool,
        large: bool,
    ):
        if r < 0:
            r = -r
            cw = not cw
        wind = -1 if (large ^ cw) else 1

        s = Vec2D(*start)
        e = Vec2D(*end)
        m = 0.5 * (s + e)
        line = e - s
        rhat = Vec2D(-line.y, line.x).normalized()
        d2 = line.dot(line)

        p0 = m + wind * sqrt(r * r - (d2 / 4)) * rhat
        self.center = p0.x, p0.y
        self.radius = r
        self.__set_angles(p0, s, e, cw)


@dataclass
class ArcPolygon(Primitive):
    """A polygon consisting of arcs instead of points in the corners.

    The ends of arcs will be connected with line segments to form a closed
    shape. Points are allowed as a "degenerate" arc where a sharp corner is
    desired, but are not required. For example, a rounded rectangle would
    consist of four arcs, but no points.

    Note that self-intersecting arc polygons are not supported.

    >>> # Rounded rectangle using four arcs
    >>> corner_radius = 2.0
    >>> arcs = [
    ...     Arc((8, 2), corner_radius, 270, 90),
    ...     Arc((8, 8), corner_radius, 0, 90),
    ...     Arc((2, 8), corner_radius, 90, 90),
    ...     Arc((2, 2), corner_radius, 180, 90),
    ... ]
    >>> rounded_rect = ArcPolygon(arcs)

    >>> # Mixed arcs and sharp corners
    >>> mixed = ArcPolygon([
    ...     Arc((0, 0), 5, 0, 90),
    ...     (10, 5),
    ...     Arc((5, 10), 3, 90, 180),
    ... ])
    """

    elements: Sequence[Arc | Point]
    """Each "corner" of the rounded polygon represented by an :py:class:`Arc`,
    the last element will be connected to the first automatically, there's no
    need to close the polygon. If there are holes in the polygon, this
    represents the outside boundary."""


@dataclass
class Polygon(Primitive):
    """A polygon consisting of 2d points.

    Line segments will connect the points to form a closed shape. Note that
    self-intersecting polygons are not supported.

    Polygons may be given holes, making it a polygon with holes.

    >>> # Triangle polygon
    >>> triangle = Polygon([(0, 0), (5, 0), (2.5, 4.33)])

    >>> # Rectangle polygon
    >>> rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])

    >>> # Polygon with a hole
    >>> outer = [(0, 0), (10, 0), (10, 10), (0, 10)]
    >>> hole = [(3, 3), (7, 3), (7, 7), (3, 7)]
    >>> donut = Polygon(outer, holes=[hole])
    """

    elements: Sequence[Point]
    """Each corner of the polygon, the last element will be connected to the
    first automatically, there's no need to close the polygon. If there are
    holes in the polygon, this represents the outside boundary."""
    holes: Sequence[Sequence[Point]] = ()
    """Optional set of holes. Each hole is a sequence of point representing an
    inner boundary. The holes must be disjoint, that is they may not intersect
    each other or the outside boundary."""


@dataclass
class PolygonSet(Primitive):
    """A set of disjoint polygons.

    >>> rect1 = Polygon([(0, 0), (5, 0), (5, 3), (0, 3)])
    >>> rect2 = Polygon([(10, 0), (15, 0), (15, 3), (10, 3)])
    >>> triangle = Polygon([(7, 5), (10, 5), (8.5, 8)])
    >>> multi_shapes = PolygonSet([rect1, rect2, triangle])
    """

    polygons: Sequence[Polygon]

    def __post_init__(self):
        assert self.polygons, "A polygon set must have at least one polygon"


@dataclass
class ArcPolyline(Primitive):
    """A polyline consisting of arcs instead of points in the corners.

    Points are allowed as a "degenerate" arc where a sharp corner is desired,
    but are not required.

    The width specifies the thickness of the polyline.

    >>> trace = ArcPolyline(0.2, [
    ...     (0, 0),
    ...     Arc((5, 0), 2, 0, 90),
    ...     (5, 10),
    ...     Arc((10, 10), 3, 90, -180),
    ... ])
    """

    width: float
    elements: Sequence[Arc | Point]


@dataclass
class Polyline(Primitive):
    """A polyline consisting of 2d points.

    The width specifies the thickness of the polyline.

    >>> trace = Polyline(0.15, [
    ...     (0, 0), (5, 0), (5, 5), (10, 5)
    ... ])
    """

    width: float
    elements: Sequence[Point]


class Circle(Primitive):
    """Create a circle primitive. Context will dictate whether the circle is a
    filled disk or a circle outline.

    Args:
        radius: Specify the radius of the disk, or, alternatively
        diameter: Specify the diameter of the disk.

    >>> # Circle by radius
    >>> small_circle = Circle(radius=5.0)

    >>> # Circle by diameter
    >>> large_circle = Circle(diameter=5.0)
    """

    radius: float
    """Radius of the circle"""

    @overload
    def __init__(self, *, radius: float): ...

    @overload
    def __init__(self, *, diameter: float): ...

    def __repr__(self):
        return f"Circle(radius={self.radius})"

    @property
    def diameter(self):
        return self.radius * 2

    def __init__(
        self,
        *,
        radius: float | None = None,
        diameter: float | None = None,
    ):
        if radius is None and diameter is None:
            raise ValueError(
                "Invalid overload when creating Circle; both radius and diameter specififed"
            )
        elif radius is not None:
            if radius < 0:
                raise ValueError(f"Radius must be positive: {radius}")
            self.radius = radius
        elif diameter is not None:
            if diameter < 0:
                raise ValueError(f"Diameter must be positive: {diameter}")
            self.radius = diameter / 2


@dataclass
class Text(Primitive):
    """A text shape.

    >>> ref_text = Text("U1", 1.0)
    >>> title = Text("Main Board Rev 2.1", 2.0, Anchor.N)
    """

    string: str
    size: float
    anchor: Anchor = Anchor.C
