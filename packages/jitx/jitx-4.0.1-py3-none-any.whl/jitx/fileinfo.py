"""
Source code location tracking
=============================

This module provides the FileInfo class for tracking where objects
were created in the source code for debugging and cross referencing purposes.
"""

from dataclasses import dataclass
from jitx.property import Property


@dataclass
class FileInfo(Property):
    """Information about where an object was created in the source code."""

    filename: str
    """The source file path."""
    line: int
    """The line number in the source file."""

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}"
