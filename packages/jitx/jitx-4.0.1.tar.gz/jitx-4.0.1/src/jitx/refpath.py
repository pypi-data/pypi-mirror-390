"""
Reference Paths
===============

When inspecting a JITX design tree, for example using
:py:func:`~jitx.inspect.visit`, the path to the element is returned as a
:py:class:`RefPath` object. This is construced as a tuple of strings, integers,
and :py:class:`Item` objects, which represent attribute access, list index
access, and mapping lookups, respectively, describing how to get from the
reference object to the element being visited.

RefPaths are normally only used for more advanced introspection use-cases and
debugging, and in most cases, a designer would not need to interact with them
directly.

>>> class A(Circuit):
...     power = Power()
...     awkward = {"a": [Port()]}

>>> circuit = A()
>>> for trace, elem in visit(circuit, Port):
...     print(trace.path, "--", repr(elem))
power -- RefPath(("power"))
power.Vp -- RefPath(("power", "Vp"))
power.Vn -- RefPath(("power", "Vn"))
awkward["a"][0] -- RefPath(("awkward", Item("a"), 0))
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence
from io import StringIO
from itertools import chain
from typing import overload


class Item:
    """A RefPath Item represents a dictionary or mapping lookup, as opposed to
    an attribute lookup or list index, which are represented by strings and
    integers, respectively."""

    def __init__(self, value: int | str):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return f"Item({repr(self.value)})"

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Item):
            return self.value == other.value
        else:
            return self.value == other


class RefPath(Sequence[str | int | Item]):
    """The path to an element in the design tree. It's made up of a tuple of
    strings, integers, and :py:class:`Item` objects, which represent attribute
    access, list index access, and mapping lookups, respectively, for
    traversing a path through a design tree."""

    def __init__(self, steps: Iterable[str | int | Item] = ()):
        self.steps = tuple(steps)

    def __len__(self):
        return len(self.steps)

    def __iter__(self):
        return iter(self.steps)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, str):
            # TODO parse other instead, and compare properly
            return str(self) == other
        elif isinstance(other, RefPath):
            return self.steps == other.steps
        else:
            return NotImplemented

    @overload
    def __getitem__(self, key: int) -> str | int | Item: ...
    @overload
    def __getitem__(self, key: slice) -> RefPath: ...

    def __getitem__(self, key):
        if isinstance(key, slice):
            return RefPath(self.steps[key])
        return self.steps[key]

    def __add__(self, other: tuple):
        return RefPath(chain(self, other))

    def __radd__(self, other: Iterable[str | int | Item]):
        return RefPath(chain(other, self))

    def __sub__(self, other: RefPath):
        """
        Return a new ``RefPath`` that is the path relative to the given path.
        If the given path is not a prefix of this path, the entire path is
        returned, and if the paths are identical or this path is a parent of
        the subtracted reference, an empty path is returned.

        If the two paths are diverging, the result is undefined.
        """
        i = 0
        N = min(len(self), len(other))
        while i < N:
            if self[i] != other[i]:
                return self[i:]
            i += 1
        return self[i:]

    def attribute(self) -> RefPath:
        """Return a new ``RefPath`` that is the path to the last attribute in
        the path, effectively stripping off trailing index and mapping lookups."""
        for i in range(len(self) - 1, 0, -1):
            if type(self[i]) is str:
                return self[i:]
        return self

    def __str__(self):
        b = StringIO()
        chained = False
        for p in self:
            if isinstance(p, Item) or not isinstance(p, str):
                b.write(f"[{p}]")
            else:
                if chained:
                    b.write(".")
                b.write(p)
            chained = True
        return b.getvalue()

    def __repr__(self):
        return f"RefPath({self.steps!r})"
