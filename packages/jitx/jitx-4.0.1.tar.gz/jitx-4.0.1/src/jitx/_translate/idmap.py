from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from itertools import count
import threading
import traceback
from typing import Any, Concatenate, ParamSpec, overload

import jitxcore._proto.local_pb2 as lpb2

from jitx import UserCodeException
from jitx._structural import Structurable, Proxy, pathstring
from jitx.inspect import Trace


class IdMapper(threading.local):
    requested_local: list[tuple[lpb2.Local, object, object, traceback.StackSummary]]
    parent_of: dict[object, object]
    trace_of: dict[object, Trace | None]
    map: dict[int, int]
    deferred: list[Callable[[], None]]
    memoized: dict[Any, int]
    filemap: dict[str, int]

    def __init__(self):
        self.clear()

    def clear(self):
        self.counter = count()
        self.map = defaultdict(lambda: next(self.counter))
        self.requested_local = []
        self.parent_of = {}
        self.trace_of = {}
        self.deferred = []
        self.memoized = {}
        self.filemap = {}

    def __call__(self, id: int) -> int:
        return self.map[id]

    def unique(self) -> int:
        return next(self.counter)

    def set_parent(self, child, parent, trace: Trace | None):
        assert child is not parent
        if child in self.parent_of:
            child_cls = Proxy.type(child).__name__
            parent_cls = Proxy.type(parent).__name__
            if parent is not self.parent_of[child]:
                parent2 = self.parent_of[child]
                parent2_cls = Proxy.type(parent2).__name__
                p1_trace = ""
                p2_trace = ""
                if trace:
                    p1_trace = f".{trace.path}"
                if child in self.trace_of:
                    child_trace = self.trace_of[child]
                    if child_trace:
                        p2_trace = f".{child_trace.path}"
                raise UserCodeException(
                    f"Child object {child} has multiple parents, found at {parent}{p1_trace} and {parent2}{p2_trace}",
                    hint=f"You should either assign {child_cls} objects to a {parent_cls} or a {parent2_cls} part of the design, but not both.",
                )
            old_trace = self.trace_of[child]
            if old_trace is None or trace is None:
                raise UserCodeException(
                    f"Child object {child} encountered multiple times in {parent}",
                    hint=f"You have assigned a {child_cls} object to a {parent_cls} multiple times, delete all assignments but one.",
                )
            new_path = trace.path
            old_path = old_trace.path
            common = min(len(old_path), len(new_path))
            old_last = old_path[-common:]
            new_last = new_path[-common:]
            if old_last != new_last:
                old_path = pathstring(old_trace.path)
                new_path = pathstring(trace.path)
                raise UserCodeException(
                    f"Child object {child} encountered multiple times in {parent}: {old_path} and {new_path}",
                    hint=f"A {child.__class__.__name__} object is part of the design twice, delete the assignment at {old_path} or at {new_path}.",
                )
        self.parent_of[child] = parent
        self.trace_of[child] = trace

    def get_filename_index(self, filename: str) -> int:
        """Get the index for a filename, creating a new index if needed."""
        if filename not in self.filemap:
            self.filemap[filename] = len(self.filemap)
        return self.filemap[filename]

    def get_filename(self, index: int) -> str:
        """Get the filename for a given index."""
        return list(self.filemap.keys())[index]

    @overload
    def memo(self, instance: Any) -> int: ...
    @overload
    def memo(self, instance: Any, id: int) -> int: ...
    def memo(self, instance: Any, id: int | None = None):
        if id is None:
            return self.memoized.get(instance, None)
        else:
            self.memoized[instance] = id
            return id

    def request_local(
        self, local: lpb2.Local, child: object, parent: object, *, empty_ok=False
    ):
        if isinstance(child, Structurable) and Structurable._disposed(child):
            raise Exception(
                "Attempting to resolve child object {child} that has been disposed."
            )
        if empty_ok and child is parent:
            local.SetInParent()
        else:
            assert child is not parent
            self.requested_local.append(
                (local, child, parent, traceback.extract_stack())
            )

    def defer(self, call: Callable[[], None]):
        self.deferred.append(call)

    def finalize(self):
        p_o = self.parent_of
        for deferred in self.deferred:
            deferred()
        for i, (local, child, parent, stack) in enumerate(self.requested_local):
            path = []
            relative = child
            target_parent: Any | None = None
            while relative is not parent:
                if not relative:
                    from ..fileinfo import FileInfo

                    traceback.print_list(stack)
                    raise Exception(
                        f"Unable to map local reference {i}, parent {parent} is not an ancestor of child {child}\nparent: {FileInfo.get(parent)}\nchild: {FileInfo.get(child)}"
                    )

                def find_parent_for(ptr: Proxy, base: Any):
                    # this is the parent in the in the parent-child table, not
                    # the proxy parent
                    parent = None
                    # this is current child we're tracking that _has_ a parent
                    # in the parent-child table
                    child = None
                    # ptr is the current "child" in the proxy chain, we're
                    # looking for a parent in that chain
                    while isinstance(ptr, Proxy):
                        if ptr is base:
                            return parent, child
                        if parent is None:
                            parent = p_o.get(ptr)
                            child = ptr
                        ptr = Proxy.of(ptr)
                    if parent is None:
                        return p_o.get(ptr), ptr
                    return parent, child

                if isinstance(relative, Proxy):
                    potential_parent, chain_element = find_parent_for(
                        relative, target_parent
                    )
                    if potential_parent is not None:
                        path.append(self(id(chain_element)))
                        target_parent = potential_parent
                    # step up the proxy chain, we do this even if we didn't
                    # find a target parent, as this happens if we traverse
                    # through a container of some kind in the proxy.
                    relative = Proxy.parent(relative)
                    if relative is None:
                        relative = target_parent
                        target_parent = None
                else:
                    path.append(self(id(relative)))
                    relative = p_o.get(relative)

            local.path.extend(reversed(path))

    def visited(self, id: int):
        return id in self.map

    def filenames(self) -> list[str]:
        return list(self.filemap.keys())


idmap = IdMapper()
P = ParamSpec("P")


def memoizer(fn: Callable[Concatenate[Any, P], int]):
    def wrapped(ob, *args: P.args, **kwargs: P.kwargs) -> int:
        ob = Proxy.forkbase(ob)
        memo = idmap.memo(ob)
        if memo is not None:
            return memo

        return idmap.memo(ob, fn(ob, *args, **kwargs))

    return wrapped


@contextmanager
def idmapper():
    idmap.clear()
    yield


def mapped(id: int) -> int:
    return idmap(id)
