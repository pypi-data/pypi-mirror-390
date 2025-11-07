"""
3D Model Representation
=======================

This module provides the Model3D class for representing 3D models with
position, scale, and rotation transforms. The 3D model is only used for export
and is otherwise not used by the JITX engine.

The 3D model file is looked up relative to the source file that calls the
Model3D constructor if a relative path is used.
"""

from ._structural import Critical
from .transform import Vec3D

import os
import os.path
import inspect


class Model3D(Critical):
    """3D model with position, scale, and rotation.

    >>> model = Model3D("APHB1608.step", rotation=(90, 0, 0))
    """

    filename: str
    """Path to the 3D model file."""
    position: Vec3D
    """3D position offset."""
    scale: Vec3D
    """3D scale factors."""
    rotation: Vec3D
    """3D rotation angles."""

    def __init__(
        self,
        filename: str,
        /,
        position: Vec3D = (0, 0, 0),
        scale: Vec3D = (1, 1, 1),
        rotation: Vec3D = (0, 0, 0),
    ):
        """Initialize a 3D model.

        Args:
            filename: Path to 3D model file. Can be absolute or relative to caller.
            position: 3D position offset. Defaults to (0, 0, 0).
            scale: 3D scale factors. Defaults to (1, 1, 1).
            rotation: 3D rotation angles. Defaults to (0, 0, 0).

        Raises:
            ValueError: If the specified file does not exist.
        """
        self.filename = (
            _relative_to_user_project_root(filename)
            if filename.startswith("{USER_PROJECT_ROOT}")
            else _relative_to_caller(filename)
        )
        if not os.path.exists(self.filename):
            raise ValueError(f"No such file: {self.filename}")
        self.position = position
        self.scale = scale
        self.rotation = rotation


def _relative_to_user_project_root(filename: str) -> str:
    """Resolve filename relative to user project root.

    Args:
        filename: Filename containing {USER_PROJECT_ROOT} placeholder.

    Returns:
        Filename with placeholder replaced by current working directory.
    """
    return filename.replace("{USER_PROJECT_ROOT}", os.getcwd())


def _relative_to_caller(filename: str) -> str:
    """Resolve filename relative to the calling file's directory.

    Args:
        filename: Relative or absolute filename.

    Returns:
        Absolute path to the file, resolved relative to the caller's directory
        if the filename is relative.
    """
    stack = inspect.stack()
    if filename[0] != "/" and len(stack) > 2:
        # stack[0] is this function relative_to_caller
        # stack[1] is the caller of relative_to_caller, which is Model3D.__init__
        # stack[2] is the caller of Model3D.__init__, where the Model3D is instantiated
        caller = stack[2]
        # caller.filename = <path>/components/MANUFACTURER/ComponentABC.py
        # Return <path>/components/MANUFACTURER/ComponentABC/<filename>
        return os.path.abspath(os.path.join(os.path.dirname(caller.filename), filename))
    else:
        return filename
