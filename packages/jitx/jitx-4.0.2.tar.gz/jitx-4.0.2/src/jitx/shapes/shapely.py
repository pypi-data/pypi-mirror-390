"""Shapely geometry integration.

This module provides the ShapelyGeometry class for integrating with the
Shapely library, allowing conversion between JITX primitive shapes and
Shapely geometric objects for advanced geometric operations.
"""

import math

import shapely
import shapely.geometry.base

from jitx.shapes import Shape, ShapeGeometry, primitive
from jitx.transform import Point, Transform

from collections.abc import Iterable
from functools import singledispatch
from typing import Literal, cast


class ShapelyGeometry(ShapeGeometry):
    """Wrapper for Shapely geometric objects.

    Provides integration between JITX shapes and the Shapely library.
    """

    def __init__(self, geometry: shapely.geometry.base.BaseGeometry):
        """Initialize with a Shapely geometry object.

        Args:
            geometry: Shapely geometry object to wrap.
        """
        self.g = geometry

    def apply(self, transform: Transform):
        """Apply a transformation to the shapely shape of this object
        Args:
            tx - Transformation to apply to the points of the shape.
              If None, this is assumed to be the `IDENTITY` transformation.
        Returns:
            A new :py:class:`~jitx.shapes.shapely.ShapelyGeometry` object with the points of the internal
            shapely geometry :py:attr:`~jitx.shapes.shapely.ShapelyGeometry.g` transformed via :py:func:`shapely.affinity` functions.
        """
        a, b, tx, d, e, ty = transform.matrix2x3(flat=True, row_major=True)
        shapely_matrix = (a, b, d, e, tx, ty)

        return ShapelyGeometry(
            shapely.affinity.affine_transform(self.g, shapely_matrix)
        )

    @classmethod
    def __to_primitive_polygon(cls, g: shapely.Polygon):
        def convert_ring(ring: shapely.LinearRing) -> list[tuple[float, float]]:
            coords = cast(list[tuple[float, float]], list(ring.coords))
            if len(coords) >= 2 and coords[0] == coords[-1]:
                coords = coords[:-1]
            return coords

        return primitive.Polygon(
            convert_ring(g.exterior),
            [convert_ring(hole) for hole in g.interiors],
        )

    def to_primitive(self) -> primitive.Primitive:
        g = self.g
        if isinstance(g, shapely.Polygon):
            # TODO holes in polygons; verify 2D coordinates
            return self.__to_primitive_polygon(g)
        elif isinstance(g, shapely.MultiPolygon):
            return primitive.PolygonSet(
                tuple(self.__to_primitive_polygon(p) for p in g.geoms)
            )

        raise ValueError(f"Unhandled shapely geometry type: {g}")

    @classmethod
    def from_shape(cls, shape: Shape, tolerance=1e-2):
        """Create ShapelyGeometry from a JITX Shape.

        Args:
            shape: JITX Shape to convert.
            tolerance: Tolerance for arc approximation.

        Returns:
            ShapelyGeometry with transform applied.
        """
        return cls.from_shapegeometry(shape.geometry, tolerance=tolerance).apply(
            shape.transform
        )

    @classmethod
    def from_shapegeometry(cls, geometry: ShapeGeometry, tolerance=1e-2):
        """Create ShapelyGeometry from any ShapeGeometry.

        Args:
            geometry: ShapeGeometry to convert.
            tolerance: Tolerance for arc approximation.

        Returns:
            ShapelyGeometry representation.
        """
        if isinstance(geometry, ShapelyGeometry):
            return geometry
        else:
            return cls.from_primitive(geometry.to_primitive(), tolerance)

    @classmethod
    def from_primitive(cls, prim: primitive.Primitive, tolerance=1e-2):
        """Create ShapelyGeometry from a primitive shape.

        Args:
            prim: Primitive shape to convert.
            tolerance: Tolerance for arc approximation.

        Returns:
            ShapelyGeometry representation of the primitive.
        """

        def arc(arc: primitive.Arc, *, trim=False):
            # polygonize inside arc that's been offset outward by half a
            # tolerance, to get a polyline that straddles the arc.
            radius = arc.radius + tolerance * 0.5
            alpha = 2 * math.acos(1 - tolerance / radius)
            sweep = math.radians(arc.arc)
            start = math.radians(arc.start)
            points = max(2, math.ceil(abs(sweep) / alpha))
            step = sweep / (points - 1)
            cx, cy = arc.center
            x = cx + arc.radius * math.cos(start)
            y = cy + arc.radius * math.sin(start)
            yield x, y
            for i in range(1, points - 1):
                th = start + i * step
                x = cx + radius * math.cos(th)
                y = cy + radius * math.sin(th)
                yield x, y
            if not trim:
                x = cx + arc.radius * math.cos(start + sweep)
                y = cy + arc.radius * math.sin(start + sweep)
                yield x, y

        def arcs(xs: Iterable[Point | primitive.Arc]):
            for x in xs:
                if isinstance(x, primitive.Arc):
                    yield from arc(x)
                else:
                    yield x

        @singledispatch
        def d(p: primitive.Primitive) -> shapely.geometry.base.BaseGeometry:
            raise ValueError(f"Unhandled primitive geometry type: {p}")

        @d.register
        def _(p: primitive.Circle):
            return shapely.polygons(
                list(arc(primitive.Arc((0, 0), p.radius, 0, 360), trim=True))
            )

        @d.register
        def _(p: primitive.Polygon):
            return shapely.polygons(p.elements)

        @d.register
        def _(p: primitive.ArcPolygon):
            return shapely.polygons(list(arcs(p.elements)))

        @d.register
        def _(p: primitive.Polyline):
            return shapely.linestrings(p.elements).buffer(p.width / 2)

        @d.register
        def _(p: primitive.ArcPolyline):
            return shapely.linestrings(list(arcs(p.elements))).buffer(p.width / 2)

        return ShapelyGeometry(d(prim))

    # Forwarding

    def __bool__(self):
        """Return True if the geometry is not empty, else False."""
        return bool(self.g)

    def __nonzero__(self):
        """Return True if the geometry is not empty, else False."""
        return bool(self.g)

    def __format__(self, format_spec):
        """Format a geometry using a format specification."""
        return self.g.__format__(format_spec)

    def __repr__(self):
        """Return a string representation of the geometry."""
        return self.g.__repr__()

    def __str__(self):
        """Return a string representation of the geometry."""
        return self.g.__str__()

    # Operators
    # ---------

    def __and__(self, other: "ShapelyGeometry"):
        """Return the intersection of the geometries."""
        return ShapelyGeometry(self.g.intersection(other.g))

    def __or__(self, other: "ShapelyGeometry"):
        """Return the union of the geometries."""
        return ShapelyGeometry(self.g.union(other.g))

    def __sub__(self, other: "ShapelyGeometry"):
        """Return the difference of the geometries."""
        return ShapelyGeometry(self.g.difference(other.g))

    def __xor__(self, other: "ShapelyGeometry"):
        """Return the symmetric difference of the geometries."""
        return ShapelyGeometry(self.g.symmetric_difference(other.g))

    # Coordinate access
    # -----------------

    @property
    def coords(self):
        """Access to geometry's coordinates (CoordinateSequence)."""
        return self.g.coords

    @property
    def xy(self):
        """Separate arrays of X and Y coordinate values."""
        return self.g.xy

    # Python feature protocol

    @property
    def __geo_interface__(self):
        """Dictionary representation of the geometry."""
        return self.g.__geo_interface__

    # Type of geometry and its representations
    # ----------------------------------------

    @property
    def wkt(self):
        """WKT representation of the geometry."""
        return self.g.wkt

    @property
    def wkb(self):
        """WKB representation of the geometry."""
        return self.g.wkb

    @property
    def wkb_hex(self):
        """WKB hex representation of the geometry."""
        return self.g.wkb_hex

    def svg(self, scale_factor=1.0, **kwargs):
        """Raise NotImplementedError."""
        return self.g.svg(scale_factor=scale_factor, **kwargs)

    def _repr_svg_(self):
        """SVG representation for iPython notebook."""
        return self.g._repr_svg_()

    @property
    def geom_type(self):
        """Name of the geometry's type, such as 'Point'."""
        return self.g.geom_type

    # Real-valued properties and methods
    # ----------------------------------

    @property
    def area(self):
        """Unitless area of the geometry (float)."""
        return self.g.area

    def distance(self, other: "ShapelyGeometry"):
        """Unitless distance to other geometry (float)."""
        return self.g.distance(other.g)

    def hausdorff_distance(self, other: "ShapelyGeometry"):
        """Unitless Hausdorff distance to other geometry (float)."""
        return self.g.hausdorff_distance(other.g)

    @property
    def length(self):
        """Unitless length of the geometry (float)."""
        return self.g.length

    @property
    def minimum_clearance(self):
        """Unitless distance a node can be moved to produce an invalid geometry (float)."""  # noqa: E501
        return self.g.minimum_clearance

    # Topological properties
    # ----------------------

    @property
    def boundary(self):
        """Return a lower dimension geometry that bounds the object.

        The boundary of a polygon is a line, the boundary of a line is a
        collection of points. The boundary of a point is an empty (null)
        collection.
        """
        return self.g.boundary

    @property
    def bounds(self):
        """Return minimum bounding region (minx, miny, maxx, maxy)."""
        return self.g.bounds

    @property
    def centroid(self):
        """Return the geometric center of the object."""
        return self.g.centroid

    def point_on_surface(self):
        """Return a point guaranteed to be within the object, cheaply.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.representative_point`.
        """
        return self.g.point_on_surface()

    def representative_point(self):
        """Return a point guaranteed to be within the object, cheaply.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.point_on_surface`.
        """
        return self.g.representative_point()

    @property
    def convex_hull(self):
        """Return the convex hull of the geometry.

        Imagine an elastic band stretched around the geometry: that's a convex
        hull, more or less.

        The convex hull of a three member multipoint, for example, is a
        triangular polygon.
        """
        return self.g.convex_hull

    @property
    def envelope(self):
        """A figure that envelopes the geometry."""
        return self.g.envelope

    @property
    def oriented_envelope(self):
        """Return the oriented envelope (minimum rotated rectangle) of a geometry.

        The oriented envelope encloses an input geometry, such that the resulting
        rectangle has minimum area.

        Unlike envelope this rectangle is not constrained to be parallel to the
        coordinate axes. If the convex hull of the object is a degenerate (line
        or point) this degenerate is returned.

        The starting point of the rectangle is not fixed. You can use
        :func:`~shapely.normalize` to reorganize the rectangle to strict
        canonical form so the starting point is always the lower left
        point.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.minimum_rotated_rectangle`.
        """
        return self.g.oriented_envelope

    @property
    def minimum_rotated_rectangle(self):
        """Return the oriented envelope (minimum rotated rectangle) of the geometry.

        The oriented envelope encloses an input geometry, such that the resulting
        rectangle has minimum area.

        Unlike :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.envelope` this rectangle is not constrained to be parallel to the
        coordinate axes. If the convex hull of the object is a degenerate (line
        or point) this degenerate is returned.

        The starting point of the rectangle is not fixed. You can use
        :func:`~shapely.normalize` to reorganize the rectangle to strict
        canonical form so the starting point is always the lower left point.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.oriented_envelope`.
        """
        return self.g.minimum_rotated_rectangle

    def buffer(
        self,
        distance,
        quad_segs=16,
        *,
        cap_style: Literal["round", "square", "flat"] = "round",
        join_style: Literal["round", "mitre", "bevel"] = "round",
        mitre_limit=5.0,
        single_sided=False,
        **kwargs,
    ):
        """Get a geometry that represents all points within a distance of this geometry.

        A positive distance produces a dilation, a negative distance an
        erosion. A very small or zero distance may sometimes be used to
        "tidy" a polygon.

        Args:
            distance: Buffer distance. Positive for dilation, negative for erosion.
            quad_segs: Number of segments for quarter circles.
            cap_style: Style for line endings.
            join_style: Style for line joins.
            mitre_limit: Limit for mitre joins.
            single_sided: Whether to buffer only one side.
            **kwargs: Additional arguments passed to Shapely.

        Returns:
            Buffered ShapelyGeometry.
        """
        return ShapelyGeometry(
            self.g.buffer(
                distance,
                quad_segs=quad_segs,
                cap_style=cap_style,
                join_style=join_style,
                mitre_limit=mitre_limit,
                single_sided=single_sided,
                **kwargs,
            )
        )

    def simplify(self, tolerance, *, preserve_topology=True):
        """Return a simplified geometry produced by the Douglas-Peucker algorithm.

        Coordinates of the simplified geometry will be no more than the
        tolerance distance from the original. Unless the topology preserving
        option is used, the algorithm may produce self-intersecting or
        otherwise invalid geometries.

        Args:
            tolerance: Maximum distance for simplification.
            preserve_topology: Whether to preserve topology.

        Returns:
            Simplified ShapelyGeometry.
        """
        return ShapelyGeometry(
            self.g.simplify(tolerance, preserve_topology=preserve_topology)
        )

    def normalize(self):
        """Convert geometry to normal form (or canonical form).

        This method orders the coordinates, rings of a polygon and parts of
        multi geometries consistently. Typically useful for testing purposes
        (for example in combination with :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.equals_exact`).
        """
        return ShapelyGeometry(self.g.normalize())

    # Overlay operations
    # ---------------------------

    def difference(self, other: "ShapelyGeometry", *, grid_size=None):
        """Return the difference of the geometries.

        Refer to `shapely.difference` for full documentation.
        """
        return ShapelyGeometry(self.g.difference(other.g, grid_size=grid_size))

    def intersection(self, other: "ShapelyGeometry", *, grid_size=None):
        """Return the intersection of the geometries.

        Refer to `shapely.intersection` for full documentation.
        """
        return ShapelyGeometry(self.g.intersection(other.g, grid_size=grid_size))

    def symmetric_difference(self, other: "ShapelyGeometry", *, grid_size=None):
        """Return the symmetric difference of the geometries.

        Refer to `shapely.symmetric_difference` for full documentation.
        """
        return ShapelyGeometry(
            self.g.symmetric_difference(other.g, grid_size=grid_size)
        )

    def union(self, other: "ShapelyGeometry", *, grid_size=None):
        """Return the union of the geometries.

        Refer to `shapely.union` for full documentation.
        """
        return ShapelyGeometry(self.g.union(other.g, grid_size=grid_size))

    # Unary predicates
    # ----------------

    @property
    def has_z(self):
        """True if the geometry's coordinate sequence(s) have z values."""
        return self.g.has_z

    @property
    def is_empty(self):
        """True if the set of points in this geometry is empty, else False."""
        return self.g.is_empty

    @property
    def is_ring(self):
        """True if the geometry is a closed ring, else False."""
        return self.g.is_ring

    @property
    def is_closed(self):
        """True if the geometry is closed, else False.

        Applicable only to linear geometries.
        """
        return self.g.is_closed

    @property
    def is_simple(self):
        """True if the geometry is simple.

        Simple means that any self-intersections are only at boundary points.
        """
        return self.g.is_simple

    @property
    def is_valid(self):
        """True if the geometry is valid.

        The definition depends on sub-class.
        """
        return self.g.is_valid

    # Binary predicates
    # -----------------

    def relate(self, other: "ShapelyGeometry"):
        """Return the DE-9IM intersection matrix for the two geometries (string)."""
        return self.g.relate(other.g)

    def covers(self, other: "ShapelyGeometry"):
        """Return True if the geometry covers the other, else False."""
        return self.g.covers(other.g)

    def covered_by(self, other: "ShapelyGeometry"):
        """Return True if the geometry is covered by the other, else False."""
        return self.g.covered_by(other.g)

    def contains(self, other: "ShapelyGeometry"):
        """Return True if the geometry contains the other, else False."""
        return self.g.contains(other.g)

    def contains_properly(self, other: "ShapelyGeometry"):
        """Return True if the geometry completely contains the other.

        There should be no common boundary points.

        Refer to :py:func:`shapely.contains_properly` for full documentation.
        """
        return self.g.contains_properly(other.g)

    def crosses(self, other: "ShapelyGeometry"):
        """Return True if the geometries cross, else False."""
        return self.g.crosses(other.g)

    def disjoint(self, other: "ShapelyGeometry"):
        """Return True if geometries are disjoint, else False."""
        return self.g.disjoint(other.g)

    def equals(self, other: "ShapelyGeometry"):
        """Return True if geometries are equal, else False.

        This method considers point-set equality (or topological
        equality), and is equivalent to (self.within(other) &
        self.contains(other)).
        """
        return self.g.equals(other.g)

    def intersects(self, other: "ShapelyGeometry"):
        """Return True if geometries intersect, else False."""
        return self.g.intersects(other.g)

    def overlaps(self, other: "ShapelyGeometry"):
        """Return True if geometries overlap, else False."""
        return self.g.overlaps(other.g)

    def touches(self, other: "ShapelyGeometry"):
        """Return True if geometries touch, else False."""
        return self.g.touches(other.g)

    def within(self, other: "ShapelyGeometry"):
        """Return True if geometry is within the other, else False."""
        return self.g.within(other.g)

    def dwithin(self, other: "ShapelyGeometry", distance):
        """Return True if geometry is within a given distance from the other.

        Refer to :py:func:`shapely.dwithin` for full documentation.
        """
        return self.g.dwithin(other.g, distance)

    ## pyright complains about no overload, unclear why.
    # def equals_exact(self, other: "ShapelyGeometry", tolerance=0.0, *, normalize=False):
    #     """Return True if the geometries are equivalent within the tolerance.

    #     Refer to :py:func:`shapely.equals_exact` for full documentation.
    #     """
    #     return self.g.equals_exact(other.g, tolerance, normalize=normalize)

    def relate_pattern(self, other: "ShapelyGeometry", pattern: str):
        """Return True if the DE-9IM relationship code satisfies the pattern."""
        return self.g.relate_pattern(other.g, pattern)

    # Linear referencing
    # ------------------

    def line_locate_point(self, other: shapely.Point, *, normalized=False):
        """Return the distance of this geometry to a point nearest the specified point.

        If the normalized arg is True, return the distance normalized to the
        length of the linear geometry.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.project`.
        """
        return self.g.line_locate_point(other, normalized=normalized)

    def project(self, other: shapely.Point, *, normalized=False):
        """Return the distance of geometry to a point nearest the specified point.

        If the normalized arg is True, return the distance normalized to the
        length of the linear geometry.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.line_locate_point`.
        """
        return self.g.project(other, normalized=normalized)

    def line_interpolate_point(self, distance, *, normalized=False):
        """Return a point at the specified distance along a linear geometry.

        Negative length values are taken as measured in the reverse
        direction from the end of the geometry. Out-of-range index
        values are handled by clamping them to the valid range of values.
        If the normalized arg is True, the distance will be interpreted as a
        fraction of the geometry's length.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.interpolate`.
        """
        return self.g.line_interpolate_point(distance, normalized=normalized)

    def interpolate(self, distance, *, normalized=False):
        """Return a point at the specified distance along a linear geometry.

        Negative length values are taken as measured in the reverse
        direction from the end of the geometry. Out-of-range index
        values are handled by clamping them to the valid range of values.
        If the normalized arg is True, the distance will be interpreted as a
        fraction of the geometry's length.

        Alias of :py:meth:`~jitx.shapes.shapely.ShapelyGeometry.line_interpolate_point`.
        """
        return self.g.interpolate(distance, normalized=normalized)

    def segmentize(self, max_segment_length):
        """Add vertices to line segments based on maximum segment length.

        Additional vertices will be added to every line segment in an input geometry
        so that segments are no longer than the provided maximum segment length. New
        vertices will evenly subdivide each segment.

        Only linear components of input geometries are densified; other geometries
        are returned unmodified.
        """
        return ShapelyGeometry(self.g.segmentize(max_segment_length))

    def reverse(self):
        """Return a copy of this geometry with the order of coordinates reversed.

        If the geometry is a polygon with interior rings, the interior rings are also
        reversed.

        Points are unchanged.
        """
        return ShapelyGeometry(self.g.reverse())
