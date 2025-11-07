from functools import singledispatch
from jitx.shapes import Shape
from jitx.shapes.primitive import (
    Arc,
    ArcPolygon,
    ArcPolyline,
    Circle,
    Empty,
    Polygon,
    PolygonSet,
    Polyline,
    Primitive,
    Text,
)
from jitx.transform import IDENTITY, Transform
import jitxcore._proto.shapes_pb2 as spb2

from jitx._translate.enums import translate_anchor
from .dispatch import warn


def normalize_angle(a):
    while a >= 360:
        a -= 360
    while a < 0:
        a += 360
    return a


def transform_arc(xf: Transform | None, arc: Arc) -> Arc:
    if not xf:
        return arc
    sx, sy = xf._scale
    # if-not to cover NaN cases
    if not (abs(abs(sx / sy) - 1) < 0.001):
        raise ValueError("Cannot transform arcs with non-uniform scaling")

    alpha = arc.start
    beta = arc.arc
    if sx < 0:
        alpha = normalize_angle(180.0 - alpha)
        beta = -beta
    if sy < 0:
        alpha = normalize_angle(360.0 - alpha)
        beta = -beta
    alpha = normalize_angle(alpha + xf._rotate)
    return Arc(xf * arc.center, abs(sx) * arc.radius, alpha, beta)


def translate_shape(shape: Shape, into: spb2.Shape):
    xf = shape.transform

    def polygonset(pset: PolygonSet):
        if not pset.polygons:
            warn("Empty polygonset shape", 2)
            into.empty_shape.SetInParent()
            return
        for polygon in pset.polygons:
            pbp = into.polygon_set.components.add()
            points = pbp.outer.points
            for pt in polygon.elements:
                pbpt = points.add()
                pbpt.x, pbpt.y = xf * pt if xf else pt
            for hole in polygon.holes:
                points = pbp.inners.add().points
                for pt in hole:
                    pbpt = points.add()
                    pbpt.x, pbpt.y = xf * pt if xf else pt

    @singledispatch
    def translate(shape: Primitive):
        warn(f"Unhandled shape {type(shape)}", 2)
        into.empty_shape.SetInParent()

    @translate.register
    def _(empty: Empty):
        into.empty_shape.SetInParent()

    @translate.register
    def _(circle: Circle):
        into.circle.center.x, into.circle.center.y = xf._translate if xf else (0, 0)
        sx, sy = xf._scale if xf else (1, 1)
        if abs(sx) != abs(sy):
            warn(f"Circle has a non-uniform scale ({sx}, {sy}) applied.")
        into.circle.radius = abs(sx * circle.radius)

    @translate.register
    def _(pset: PolygonSet):
        polygonset(pset)

    @translate.register
    def _(polygon: Polygon):
        if polygon.holes:
            polygonset(PolygonSet((polygon,)))
        else:
            if not polygon.elements:
                warn("Empty polygon", 2)
                into.empty_shape.SetInParent()
                return
            points = into.polygon.points
            for pt in polygon.elements:
                point = points.add()
                point.x, point.y = xf * pt if xf else pt

    @translate.register
    def _(arc_polygon: ArcPolygon):
        elements = into.arc_polygon.elements
        for elem in arc_polygon.elements:
            element = elements.add()
            if isinstance(elem, tuple):
                element.point.x, element.point.y = xf * elem if xf else elem
            elif isinstance(elem, Arc):
                translate_arc(transform_arc(xf, elem), element.arc)

    @translate.register
    def _(polyline: Polyline):
        into.polyline.width = polyline.width
        points = into.polyline.points
        for pt in polyline.elements:
            point = points.add()
            point.x, point.y = xf * pt if xf else pt

    @translate.register
    def _(arc_polyline: ArcPolyline):
        into.arc_polyline.width = arc_polyline.width
        for elem in arc_polyline.elements:
            element = into.arc_polyline.elements.add()
            if isinstance(elem, tuple):
                element.point.x, element.point.y = xf * elem if xf else elem
            elif isinstance(elem, Arc):
                translate_arc(transform_arc(xf, elem), element.arc)

    @translate.register
    def _(text: Text):
        into.text.string = text.string
        # text size cannot be negative
        into.text.size = abs(xf._scale[1] * text.size)
        into.text.anchor = translate_anchor(text.anchor)
        translate_pose(xf or IDENTITY, into.text.pose)

    translate(shape.geometry.to_primitive())


def translate_pose(xf: Transform, into: spb2.Pose):
    into.center.x, into.center.y = xf._translate
    into.angle = xf._rotate
    into.flipx = xf._scale[0] < 0


def translate_arc(arc: Arc, into: spb2.Arc):
    into.center.x, into.center.y = arc.center
    into.radius = arc.radius
    into.start_angle = arc.start
    into.angle = arc.arc
