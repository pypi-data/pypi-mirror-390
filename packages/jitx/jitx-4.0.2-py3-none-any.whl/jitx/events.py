"""
Event System
============

This module declares the JITX event system for triggering behavior at specific
points during design processing and instantiation.
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
import inspect
from typing import Any, Self, TypeVar

from .context import Context
from ._structural import PrePostInit
from ._instantiation import InstantiationStructure, instantiation

import sys

if sys.version_info > (3, 13):
    T = TypeVar("T", default=None)


class Event[T]:
    """Events can be used to trigger various behavior throughout your design,
    such as verifying a particular condition after the design has been fully
    instantiated.

    Some events are predefined and will be triggered automatically by the
    framework, and user defined events have to be triggered manually. Subclass
    this class to create a user defined event.
    """

    @classmethod
    def on(
        cls, method: Callable[[Any, Self], T] | Callable[[Self], T] | Callable[[], T]
    ):
        """Register a method to be called when this event fires. The method
        should accept an instance of the event as argument.

        The method will be called with the context set to the same context that
        was enabled when the method was registered.

        >>> class MyComponent(Component):
                @Design.Initialized.on
                def on_initialized(self, init: Design.Initialized):
                    ... # do something after initialization
        """
        if instantiation.active():
            ec = EventContext.require()
            ec.events[cls].append((method, instantiation.current_frame))
            return method
        else:

            def register(ob, _):
                m = method.__get__(ob, type(ob))
                ec = EventContext.require()
                ec.events[cls].append((m, instantiation.current_frame))
                return method

            return PrePostInit(register, lambda _, ob: ob)

    def fire(self):
        """Fire this event.

        Note that firing predefined events when they're not expected may cause
        unpredictable results as internal infrastructure may rely on them.

        >>> @dataclass
        ... class MyEvent(Event):
                some_field: str

        >>> class MyComponent(Component):
        ...     @MyEvent.on
        ...     def my_event_handler(self, myevent):
        ...         print(f"Hello {myevent.some_field}!")
        ...
        ...     @Design.Initialized.on
        ...     def on_initialized(self):
        ...         MyEvent("World").fire()
        """
        ec = EventContext.require()
        cls = self.__class__
        if cls in ec.events:
            for recv, frame in ec.events[cls]:
                with instantiation.frame(frame):
                    if inspect.signature(recv).parameters:
                        recv(self)
                    else:
                        recv()


@dataclass
class EventContext(Context):
    """Context for managing event handlers during design processing."""

    events: dict[type[Event], list[tuple[Callable, InstantiationStructure.Frame]]] = (
        field(default_factory=lambda: defaultdict(list))
    )
