"""
Memoization decorators
======================

This module provides decorators for enabling and disabling memoization on
structural classes to optimize object creation. Generally users will not
interact directly with these decorators, as the effects of them can be
unintuitive.
"""

from jitx._structural import Structural


def memoize[T: Structural](cls: type[T]) -> type[T]:
    """Decorator to enable memoization on this class and its subclasses. This
    is the default for many structural elements and doesn't need to be
    explicitly added."""
    if not issubclass(cls, Structural):
        raise TypeError("Memoization currently only possible for structural elements")
    cls._memoize(True)
    return cls


def dememoize[T: Structural](cls: type[T]) -> type[T]:
    """Decorator to disable memoization on this class and its subclasses. This
    is useful if the object is reactive and changes based on the context in
    which it's being used, and thus cannot be memoized based on its arguments."""
    if not issubclass(cls, Structural):
        raise TypeError("Memoization currently only possible for structural elements")
    cls._memoize(False)
    return cls
