"""
Errors and Exceptions
=====================

This module provides exception classes for handling errors during design
processing and validation.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ._structural import RefPath


class UserCodeException(Exception):
    """
    Exception raised when user code appears to have constructed an invalid
    design structure.
    """

    hint: str | None

    def __init__(self, message: str, hint: str | None = None):
        super().__init__(message)
        self.hint = hint


class InstantiationException(Exception):
    """This error is raised if an object cannot be instantiated."""


class InvalidElementException(Exception):
    """This error is raised if a "critical" element is encountered in an
    unexpected place in the design tree. As an example, if we encounter a
    :py:class:`~jitx.net.Pin` object is encountered in a
    :py:class:`~jitx.circuit.Circuit` object, this error would be raised. In
    the best case the element is spurious and could just be ignored as having
    no effect, but more commonly, this is a mistake and should be corrected
    thus we treat this as an error.
    """

    element: Any
    "The encountered element"
    path: RefPath
    "The path where it was encountered"
    container: Any
    "The parent object that contained the element"

    def __init__(self, element: Any, path: RefPath, container: Any):
        """Initialize the exception with the invalid element details.

        Args:
            element: The invalid element that was encountered.
            path: The path where the element was found.
            container: The parent object containing the element.
        """
        self.element = element
        self.path = path
        self.container = container

    def __str__(self):
        from ._structural import pathstring

        # name = type(ob).__module__ + '.' + type(ob).__name__
        # basename = type(base).__module__ + '.' + type(base).__name__
        name = type(self.element).__name__
        inside = type(self.container).__name__
        return f"{name} element {pathstring(self.path)} has no effect inside {inside} and is invalid."
