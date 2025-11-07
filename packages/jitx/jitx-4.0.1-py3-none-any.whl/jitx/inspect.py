"""
JITX Object Introspection
=========================

The JITX object introspection is based on traversing the design tree using the
:py:func:`~jitx.inspect.visit` function. Other utility and helper functions are
also provided but they all rely on the :py:func:`~jitx.inspect.visit` function
to do the traversal.
"""

from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from types import UnionType
from typing import get_args, get_origin, overload, Any

from .container import Composite
from .transform import IDENTITY, Transform
from .placement import Kinematic

from ._structural import Proxy, Ref, Structural, RefPath as RefPath, traverse_base


_empty_path = RefPath()


@overload
def visit[T: UnionType](
    root,
    types: T,
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    path: RefPath = _empty_path,
    transform: Transform | None = IDENTITY,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs: bool = False,
    filter: Callable[[T], bool] | None = None,
) -> Generator[tuple[Trace, T], None, None]: ...


@overload
def visit[T](
    root,
    type: type[T] | tuple[type[T], ...],
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    path: RefPath = _empty_path,
    transform: Transform | None = IDENTITY,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs: bool = False,
    filter: Callable[[T], bool] | None = None,
) -> Generator[tuple[Trace, T], None, None]: ...


def visit(
    root,
    types: type | tuple[type, ...] | UnionType,
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    path: RefPath = _empty_path,
    transform: Transform | None = IDENTITY,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs: bool = False,
    filter: Callable[[Any], bool] | None = None,
):
    """Find elements in an object structure. Objects of the specified ``types``
    will be returned, traversing down through the object tree structure. If
    ``through`` is specified the traversal will only pass through those when
    looking for matching elements, otherwise all JITX structural elements will
    be traversed.

    Args:
        root: The root object to start traversing
        types: A type, tuple of types, or union of types to find
        through: Optional argument to limit which objects to recurse through.
            If undefined, only :py:class:`~jitx._structural.Structural`
            elements will be visited.
        path: Optional starting path
        transform: Optional starting transform, if unset will default to the
            identity transform. Set to None to suppress computing transforms.
        opaque: Optional argument to limit which objects to recurse through.
            If unspecified, or None, contents of
            :py:class:`~jitx._structural.Ref` elements will be skipped. To
            recurse through all structural elements, including Ref elements,
            set this to an empty tuple.
        filter: Optional filter function to apply to the elements. Only elements
            that pass the filter will be returned.

    Yields:
        Pairs of :py:class:`~Trace` to the element, and the element itself.
    """
    if through is None:
        through = (Structural,)
    elif isinstance(through, UnionType):
        through = get_args(through)

    if transform is not None:
        # make sure we stop at these to grab the transform
        through = through + (Composite,)

    if isinstance(types, type):
        types = (types,)
    elif isinstance(types, UnionType):
        types = get_args(types)
    elif get_origin(types) is not None:
        origin_type = get_origin(types)
        if isinstance(origin_type, type):
            types = (origin_type,)
        else:
            raise ValueError("Unsupported visit type: {types}")

    types = tuple(get_origin(t) or t for t in types)
    for t in types:
        if not isinstance(t, type):
            raise ValueError("Unsupported visit type: {t}")

    if opaque is None:
        opaque = (Ref,)

    checktypes = through + types
    visited = set()

    def _visit(
        root_path: RefPath,
        ob: Any,
        xform: Transform | None,
        trace: Trace | None,
        id_path: set[int],
    ):
        for path, elem in traverse_base(ob, checktypes, (), root_path, refs=refs):
            if refs:
                # use id to bypass unhashable issues
                if id(elem) in visited:
                    continue
                visited.add(id(elem))
            xf = xform
            # isinstance(Kinematic) for proxies doesn't work, since Kinematic
            # doesn't use that meta class.
            if xf is not None and issubclass(Proxy.type(elem), Kinematic):
                transform = elem.transform
                if transform is not None:
                    xf = xf * transform
            if issubclass(Proxy.type(elem), types):
                # do not use xf here, as it'll have elem's transform applied
                if filter is None or filter(elem):
                    yield Trace(path, xform, ob, trace), elem
            if issubclass(Proxy.type(elem), through) and not issubclass(
                Proxy.type(elem), opaque
            ):
                if id(elem) in id_path:
                    raise ValueError(f"Cycle detected for object {ob} at {path}")
                id_path.add(id(elem))
                yield from _visit(
                    path, elem, xf, Trace(path, xform, ob, trace), id_path
                )
                id_path.remove(id(elem))

    return _visit(path, root, transform, None, set())


@dataclass
class Trace:
    """The Trace inspection object represents a path through the design tree to
    reach a particular element, it is returned by the :py:func:`visit` function."""

    path: RefPath
    """The path to the element."""

    transform: Transform | None
    """The accumulated transform leading up to this element, or None if one
    could not be determined. Note that the element's own transform, if it has
    one, is not included in this transform."""

    parent: Any = None
    """The parent structural element."""

    trace: Trace | None = None
    """The trace to the parent object, if any."""


@overload
def decompose[T](
    ob,
    type: type[T],
    /,
    *,
    refs=False,
    filter: Callable[[T], bool] | None = None,
) -> Generator[T, None, None]: ...


@overload
def decompose(
    ob,
    types: tuple[type, ...] | UnionType,
    /,
    *,
    refs=False,
    filter: Callable[[Any], bool] | None = None,
) -> Generator[Any, None, None]: ...


def decompose(
    ob,
    types: type | tuple[type, ...] | UnionType,
    /,
    *,
    refs=False,
    filter: Callable[[Any], bool] | None = None,
):
    """Collect fields of a type or types into a sequence that can be used for
    deconstruction assignment.  The elements are all semi-shallow children,
    traversing lists and dicts, but not other structural elements. Note that
    objects of subtypes can be returned as well.

    >>> class A:
    ...     other = "field"
    ...     ports = [Port(), DiffPair()]
    ...     another = GPIO()
    >>> p1, p2, p3 = decompose(A(), Port)
    >>> type(p1) is Port and type(p2) is DiffPair and type(p3) is GPIO
    True
    """
    return extract(ob, types, through=(), refs=refs, filter=filter)


@overload
def extract[T](
    ob,
    type: type[T],
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs=False,
    filter: Callable[[T], bool] | None = None,
) -> Generator[T, None, None]: ...


@overload
def extract(
    ob,
    types: tuple[type, ...] | UnionType,
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs=False,
    filter: Callable[[Any], bool] | None = None,
) -> Generator[Any, None, None]: ...


def extract(
    ob,
    types: type | tuple[type, ...] | UnionType,
    /,
    through: tuple[type, ...] | UnionType | None = None,
    *,
    opaque: tuple[type, ...] | UnionType | None = None,
    refs=False,
    filter: Callable[[Any], bool] | None = None,
):
    """Recursively traverse all objects in the tree and yield all objects of a
    particular type or types. This is similar to :py:func:`~visit`, but does
    not generate the meta information associated with each returned element.

    >>> def component_ports(comp:Component) -> list[Port]:
    ...     return list(extract(comp, Port))
    """
    for _, elem in visit(
        ob, types, through, transform=None, opaque=opaque, filter=filter, refs=refs
    ):
        yield elem
