from contextlib import contextmanager
from functools import singledispatch
from jitx.inspect import Trace, visit
from jitx._structural import (
    Critical,
    Proxy,
    RefPath,
    pathstring,
)
from jitx.error import InvalidElementException

import os.path
import warnings

from jitx.transform import IDENTITY

_warn_skips = (os.path.dirname(__file__),)


def warn(string, stacklevel=0):
    warnings.warn(string, skip_file_prefixes=_warn_skips, stacklevel=stacklevel + 1)


class DispatchQueue:
    def __init__(self):
        self.queue = []


def queue_dispatch(base, element):
    dpq = getattr(base, "_dispatch__queue", None)
    if dpq is None:
        dpq = DispatchQueue()
        base._dispatch__queue = dpq
    elif not isinstance(dpq, DispatchQueue):
        raise TypeError(f"Internal State Error: {dpq} is not a dispatch queue")
    dpq.queue.append(element)


@contextmanager
def dispatch(
    base,
    *,
    ignore_critical=False,
    base_path: Trace | RefPath | None = None,
):
    @singledispatch
    def dispatcher(ob, trace: Trace) -> None:
        if isinstance(ob, Proxy):
            dispatcher.dispatch(Proxy.type(ob))(ob, trace)
        else:
            warn(
                f"Dispatched unhandled type {type(ob).__name__} at {pathstring(trace.path)}: {ob}",
                2,
            )

    yield dispatcher

    if not ignore_critical:

        @dispatcher.register
        def _(ob: Critical, trace: Trace) -> None:
            raise InvalidElementException(ob, trace.path, base)

    types = tuple(set(dispatcher.registry.keys()) - {object})
    transform = IDENTITY
    if isinstance(base_path, Trace):
        transform = base_path.transform
        base_path = base_path.path
    for trace, ob in visit(
        base, types, path=base_path or RefPath(), through=(), transform=transform
    ):
        dispatcher(ob, trace)

    dpq = getattr(base, "_dispatch__queue", None)
    if isinstance(dpq, DispatchQueue):
        while dpq.queue:
            q = dpq.queue
            dpq.queue = []
            for x in q:
                dispatcher(x, Trace(path=RefPath(), transform=None))
