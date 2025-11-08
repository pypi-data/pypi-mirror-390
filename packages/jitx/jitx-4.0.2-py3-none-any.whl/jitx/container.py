"""
Container classes
=================

This module provides container classes for organizing and composing objects,
along with decorators for inline instantiation and inner class handling.
Containers effectively provide namespaces for organizing objects, and the
contained objects are considered direct members of the object that the
container is a member of. This allows the container to organize objects that
are only valid in certain contexts.
"""

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Self, overload
from ._structural import (
    Container as _Container,
    Proxy,
    Ref as Ref,
    Structurable as _Structurable,
)
from .transform import Point, Transform
from .placement import Kinematic


# redeclare here for documentation purposes, _structural doesn't show up in the documentation.
class Container(_Container):
    """Namespace-like container object, will be traversed in all introspection. Can have any attribute set."""

    if TYPE_CHECKING:
        # the existence these methods tell the type checker that the can
        # container can both get and set dynamic attributes; the default
        # behavior for these are fine, and defining them at runtime can cause
        # issues with subclassing, should they need to declare them too, thus
        # we only declare these while type checking.

        def __setattr__(self, key, value):
            super().__setattr__(key, value)

        def __getattr__(self, key):
            raise AttributeError(key)


class Structurable(_Structurable):
    """Structurable container object that supports instantiation in class contexts."""


class Composite(Container, Kinematic[Transform]):
    """Create a geometric composition of objects. This allows the construction
    of, for example, a landpattern with a part being constructed in its own
    frame of reference, or a complex symbol to be constructed by composing
    multiple elements into one.

    >>> class MyLandpattern(Landpattern):
    ...     pad1 = MyPad().at(-0.5, 0)
    ...     pad2 = MyPad().at(0.5, 0)
    ...     courtyard = Courtyard(rectangle(2, 1))
    ...
    ...     def __init__(self):
    ...         plus = plus_symbol(0.5, 0.1)
    ...         self.plus = Silkscreen(plus.at(0, 1))
    ...         self.composite = Composite(Transform.rotate(45))
    ...         self.composite.plus = Silkscreen(plus.at(math.sqrt(2)/2, math.sqrt(2)/2))
    """

    def __init__(self, transform: Transform):
        """Initialize a geometric composition with the given transform.

        Args:
            transform: The transformation to apply to the composed objects.
        """
        self.transform = transform

    @overload
    def at(self, point: Point, /, *, rotate: float = 0) -> Self: ...
    @overload
    def at(self, xform: Transform, /) -> Self: ...
    @overload
    def at(self, x: float, y: float, /, *, rotate: float = 0) -> Self: ...

    def at(
        self,
        x: Transform | Point | float,
        y: float | None = None,
        /,
        *,
        rotate: float = 0,
    ):
        """Place this object relative to its frame of reference. Note that this
        modifies the object, and does not create a copy.

        Args:
            x: x-value, transform, or placement to adopt.
            y: y-value if x is an x-value. This argument is only valid in that context.
        Returns:
            the object itself."""
        if isinstance(x, Transform):
            xform = x.clone()
        elif isinstance(x, tuple):
            assert y is None
            xform = Transform(x, rotate)
        else:
            assert isinstance(y, float | int)
            xform = Transform((x, y), rotate)
        if isinstance(self, Proxy):
            # setting the transform does not taint the proxy.
            with Proxy.override():
                self.transform = xform
        else:
            self.transform = xform
        return self


def inline[T](cls: type[T]) -> T:
    """Decorator to create a single instance of a class, and replace the class
    with that instance. Useful for one-of classes, such as the main circuit of
    a design or a component that has a unique symbol or landpattern that is
    unlikely to be reused.

    >>> class MyDesign(Design):
    ...     @inline
    ...     class Main(Circuit):
    ...         component = ImportantComponent()
    """
    return cls()


def inner[**P, T](cls: Callable[P, T]) -> Callable[P, T]:
    """Decorator to automatically pass on the outer class' instance to the
    inner class. The inner class' ``__init__`` method must accept the outer
    class as the first argument after ``self`` as this effectively creates an
    instance method in the outer class, that creates an instance of the inner
    class.

    Here's a truncated example of it being used in the JITX's standard library
    USB protocol

    >>> @dataclass(frozen=True)
    ... class USBStandard:
    ...     skew: Toleranced
    ...     impedance: Toleranced
    ...     loss: float = 12.0
    ...
    ...     @inner
    ...     class Constraint[T: USB2](SignalConstraint[T]):
    ...         "Construct a :py:class:`SignalConstraint` applicable to USB topologies of this standard."
    ...
    ...         def __init__(
    ...             self,
    ...             std: USBStandard,
    ...             structure: DifferentialRoutingStructure | None = None,
    ...         ) -> None:
    ...             self.diffpair_constraint: DiffPairConstraint = DiffPairConstraint(skew: std.skew, loss: std.loss, structure: structure)

    >>> class USB(USBStandard, Enum):
    ...     v2 = Toleranced(0, 3.75e-12), Toleranced.percent(90, 15)
    ...     v3 = Toleranced(0, 1e-12), Toleranced.percent(90, 15)
    ...     v4 = Toleranced(0, 1e-12), Toleranced(85, 9)

    >>> USB.v2.Constraint()
    <Constraint object>
    """

    @wraps(cls)
    def method(*args: P.args, **kwargs: P.kwargs):
        return cls(*args, **kwargs)

    return method
