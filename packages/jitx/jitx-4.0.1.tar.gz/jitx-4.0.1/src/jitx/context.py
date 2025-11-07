"""
Contexts
========

This module provides context management classes for maintaining state during
design processing and instantiation. Contexts can be set to provide a value for
a particular subtree of the design. If a context object is created in the class
body, it will be set first, before any of the other fields are initialized,
which means that subcircuits or components will see the new context value.

If a context is needed as part of the function, it does not need to be assigned
to a member field, and indeed doing so does not set the context value, instead
it is activated using a ``with`` block.
"""

from collections.abc import Callable
from typing import cast

from ._instantiation import instantiation


class Context:
    """Base class for context objects that maintain state during processing.

    Context objects can be used as context managers to automatically push and
    pop context state, ensuring proper cleanup.
    """

    def set(self):
        """Set this context as the current active context."""
        instantiation.set(self.__class__, self)

    @classmethod
    def get[T: Context](cls: type[T]) -> T | None:
        """Get the current active context of this type.

        Returns:
            The current context instance, or None if not set.
        """
        from ._structural import instantiation

        return cast(T | None, instantiation.get(cls))

    @classmethod
    def require[T: Context](cls: type[T]):
        """Get the current active context of this type, raising an error if not set.

        Returns:
            The current context instance.

        Raises:
            ValueError: If no context of this type is currently active.
        """
        val = cls.get()
        if val is None:
            raise ValueError(f"Context {cls.__name__} is not available")
        return cast(T, val)

    def __enter__(self):
        """Enter the context manager, pushing a new context frame."""
        instantiation.push()
        self.set()

    def __exit__(self, typ, value, tb):
        """Exit the context manager, popping the context frame."""
        instantiation.pop()


# Helper class to build a directory of context accessors, e.g.
# class DesignContext:
#     def __init__(self):
#         self.substrate = ContextProperty(SubstrateContext)
# design = DesignContext()
# ...
# now accessing design.substrate will give the current substrate.
class ContextProperty[T: Context, S]:
    """Property descriptor for accessing context objects.

    Creates a property that automatically retrieves the current context
    and optionally applies a field accessor function.

    >>> class DesignContext:
    ...     def __init__(self):
    ...         self.substrate = ContextProperty(SubstrateContext)
    >>> design = DesignContext()
    >>> # Accessing design.substrate will get the current substrate context
    """

    def __init__(self, context: type[T], field: Callable[[T], S] = lambda x: x):
        """Initialize a context property.

        Args:
            context: The context class to retrieve.
            field: Optional function to extract a field from the context.
        """
        self.context = context
        self.field = field

    def __get__(self, instance, owner):
        """Get the context value, applying the field accessor if provided."""
        return self.field(self.context.require())

    def __set__(self, instance, value):
        """Implemented to allow += to work, will only accept the same object as
        already present in the context."""
        if value is not self.field(self.context.require()):
            raise AttributeError("Context properties cannot be replaced")
