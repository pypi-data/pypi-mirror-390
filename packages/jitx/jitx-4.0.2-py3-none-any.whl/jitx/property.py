"""
Property system
===============

This module provides the base Property class. Objects can be assigned properties,
and properties can be retrieved from objects.
"""

from collections.abc import Iterable
from typing import Any, overload
from ._structural import Structural, Proxy


class Property:
    """Property base class. To declare a new property, subclass this class. Note that
    properties should be immutable, or care should be taken that a mutable
    property is not reused across multiple objects (unless intentional, of
    course). For example a property holding a list of things to be appended to
    per object should be carefully constructed so the same list is not attached
    to multiple objects.

    >>> @dataclass(frozen=True)
    ... class MyProperty(Property):
    ...     some_string_value: str

    >>> other_object = object()  # some object to assign property, such as a Port
    >>> MyProperty("abc").assign(other_object)
    >>> MyProperty.get(other_object)
    MyProperty(some_string_value="abc")
    """

    def assign(self, *objects: Any):
        # bypass proxy forwarding
        with Proxy.override():
            for obs in objects:
                if not isinstance(obs, Iterable) or isinstance(obs, Structural):
                    obs = (obs,)
                for ob in obs:
                    props = getattr(ob, "_Property__dict", None)
                    if not props:
                        props = {}
                        # bypass frozen checks
                        object.__setattr__(ob, "_Property__dict", props)
                    t = type(self)
                    props[t] = self._set(props.get(t))

    # Any|None here to indicate that it will be called with an object of its
    # own type or None, but can't use Self here since that would make the type
    # signature incompatible.
    def _set(self, other: Any | None):
        # can be used to make sure a list-property is unique by cloning on set
        return self

    @overload
    @classmethod
    def get[T, D](cls: type[T], ob: Any, default: D) -> T | D: ...

    @overload
    @classmethod
    def get[T](cls: type[T], ob: Any) -> T | None: ...

    @classmethod
    def get[T, D](cls: type[T], ob: Any, default: D | None = None) -> T | D:
        props = getattr(ob, "_Property__dict", {})
        return props.get(cls, default)
