"""
Shapes and geometry
===================

This module provides the core :py:class:`Shape` and :py:class:`ShapeGeometry`
classes for representing geometric objects with optional transformations.
Shapes can be converted between different representations (primitive, shapely)
and positioned using transforms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, overload
from .._structural import passive_representation

if TYPE_CHECKING:
    from jitx.transform import Point, Transform
    from .primitive import Primitive


CoShapeGeometry = TypeVar("CoShapeGeometry", bound="ShapeGeometry", covariant=True)


class Shape(Generic[CoShapeGeometry]):
    """A shape with geometry and an optional transform.

    Shapes combine geometric data with positioning information, allowing
    geometric objects to be placed and transformed in 2D space.
    """

    geometry: CoShapeGeometry
    """The geometric data for this shape."""
    transform: Transform
    """The transformation applied to the geometry."""

    def __init__(self, geometry: CoShapeGeometry, transform: Transform | None):
        """Initialize a shape with geometry and optional transform.

        Args:
            geometry: The geometric data.
            transform: Optional transformation. Defaults to identity if None.
        """
        # avoid cyclic dependency on load
        from jitx.transform import ImmutableTransform

        self.geometry = geometry
        if not transform:
            from jitx.transform import IDENTITY

            self.transform = IDENTITY
        elif isinstance(transform, ImmutableTransform):
            self.transform = transform
        else:
            self.transform = transform.clone()

    if passive_representation:
        # hide raw static data when generating documentation
        def __repr__(self):
            return f"Shape[{type(self.geometry).__name__}]"
    else:

        def __repr__(self):
            return f"Shape({repr(self.geometry)}, {self.transform!r})"

    def to_shapely(self):
        """Convert the given shape into a 'shapely' native format including the transform.

        Returns:
            A :py:class:`~jitx.shapes.shapely.ShapelyGeometry` shape with all of the points of the geometry transformed
            by the :py:attr:`~jitx.shapes.Shape.transform` project of this shape.
        """
        from jitx.shapes.shapely import ShapelyGeometry

        return ShapelyGeometry.from_shape(self)

    def to_primitive(self) -> Shape[Primitive]:
        """Convert the given shape into a :py:class:`~jitx.shapes.primitive.Primitive` shape.

        Returns:
            A :py:class:`~jitx.shapes.primitive.Primitive` shape with all of the points of the geometry transformed
            by the :py:attr:`~jitx.shapes.Shape.transform` project of this shape.
        """
        return Shape(self.geometry.to_primitive(), self.transform)

    def __matmul__(self, where: Point | Transform) -> Shape[CoShapeGeometry]:
        return self.at(where)

    @overload
    def at(
        self, x: float, y: float, /, *, rotate: float = 0, scale: float = 1
    ) -> Shape[CoShapeGeometry]: ...
    @overload
    def at(
        self, vector: Point, /, *, rotate: float = 0, scale: float = 1
    ) -> Shape[CoShapeGeometry]: ...
    @overload
    def at(self, transform: Transform, /) -> Shape[CoShapeGeometry]: ...

    def at(
        self,
        x: float | Point | Transform,
        y: float | None = None,
        /,
        *,
        rotate: float = 0,
        scale: float = 1,
    ) -> Shape[CoShapeGeometry]:
        """Create a new shape with additional positioning transform.

        Args:
            x: X coordinate, point, or transform to apply.
            y: Y coordinate if x is a coordinate.

        Returns:
            New shape with the additional transform applied.
        """
        from jitx.transform import Transform

        if y is None:
            if isinstance(x, Transform):
                return Shape(self.geometry, x * self.transform)
            assert isinstance(x, tuple)
            return Shape(
                self.geometry, Transform(x, rotate, (scale, scale)) * self.transform
            )
        else:
            assert isinstance(x, float | int)
            return Shape(
                self.geometry,
                Transform((x, y), rotate, (scale, scale)) * self.transform,
            )


class ShapeGeometry(ABC, Shape):
    """Shape geometry is raw shape information, without a transform."""

    def __init__(self):
        # do not call super().__init__(), the shape's fields are replaced by
        # read-only properties.
        pass

    # Crutch to allow shape geometry to be used as a shape. It's not strictly
    # type safe, since it's not a field but a property.
    @property
    def geometry(self):  # type: ignore
        return self

    @geometry.setter
    def geometry(self, value):  # type: ignore that this is a property overloading the base
        raise ValueError(
            "Can't mutate the geometry of a ShapeGeometry object. Use Shape instead."
        )

    @property
    def transform(self):  # type: ignore
        from jitx.transform import IDENTITY

        return IDENTITY

    @transform.setter
    def transform(self, value):  # type: ignore
        raise ValueError(
            "Can't mutate the transform of a ShapeGeometry object. Use .at() to create a Shape instead."
        )

    @abstractmethod
    def to_primitive(self) -> Primitive: ...

    def __repr__(self):
        return f"{type(self).__name__}()"
