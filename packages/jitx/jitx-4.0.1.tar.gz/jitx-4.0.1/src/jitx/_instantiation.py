from threading import local
from typing import Self, Any
from contextlib import contextmanager

import os


class InstantiationStructureException(Exception):
    pass


class InstantiationStructure:
    class Frame:
        def __init__(self, parent: Self | None = None):
            self.parent = parent
            self.context: dict[Any, Any] = {}
            self.tracker: list[dict[Any, Any]] = []

        def get(self, key):
            if key in self.context:
                value = self.context[key]
            elif self.parent:
                value = self.parent.get(key)
            else:
                value = None
            if self.tracker:
                self.tracker[-1][key] = value
            return value

    class InstantiationData(local):
        def __init__(self):
            super().__init__()
            self.stack: list[InstantiationStructure.Frame] = []

    def __init__(self):
        self.data = self.InstantiationData()
        self.generation = 0

    def active(self):
        return bool(self.data.stack)

    @contextmanager
    def activate(self):
        if self.active():
            raise InstantiationStructureException("Structure already active")
        # for tracking lost objects
        self.generation += 1
        self.data.stack.append(self.Frame())
        try:
            yield
        finally:
            self.data.stack.clear()

    @contextmanager
    def require(self):
        if self.active():
            yield
        else:
            with self.activate():
                yield

    @contextmanager
    def frame(self, frame: Frame | None = None):
        self.push(frame)
        try:
            yield
        finally:
            self.pop()

    def push(self, frame: Frame | None = None):
        if not self.active():
            raise InstantiationStructureException("Structure not active")
        if frame is None:
            frame = self.Frame(self.data.stack[-1])
        self.data.stack.append(frame)

    def pop(self):
        self.data.stack.pop()

    @property
    def current_frame(self) -> Frame:
        if not self.active():
            raise InstantiationStructureException("Structure not active")
        return self.data.stack[-1]

    def get(self, key):
        if not self.active():
            raise InstantiationStructureException("Structure not active")
        return self.data.stack[-1].get(key)

    def set(self, key, value):
        if not self.active():
            raise InstantiationStructureException("Structure not active")
        self.data.stack[-1].context[key] = value


instantiation = InstantiationStructure()
passive_representation = False
if os.environ.get("JITX_PASSIVE_INSTANTIATION"):
    # this is used to show representation of instantiable objects as their class
    # name, rather than their "Instantiable" wrapper. The purpose of this is to
    # get legible documentation. Enabling this during a debug sessions will
    # likely be confusing, if there's a spurious "Instantiable" object causing
    # whatever bug is being debugged.
    passive_representation = True
