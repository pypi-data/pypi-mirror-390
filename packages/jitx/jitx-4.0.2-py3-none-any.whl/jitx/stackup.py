"""
Design Stackup
==============

This module provides classes for defining board layer stackups,
including materials, dielectrics, and conductors.
"""

from __future__ import annotations
from collections.abc import Sequence
from typing import ClassVar

from jitx._structural import Critical, RefTuple
from jitx.inspect import decompose


class Stackup(Critical):
    """Stackups are determined by introspection, layers will be declared in the
    order they are specified in the stackup. Can be specified by an ordered set
    of attributes, or containers such as lists, or a combination thereof.

    >>> class SoldermaskLayer(Dielectric):
    ...     dielectric_coefficient = 1.5
    ...     loss_tangent = 0.01
    >>> class FR4(Dielectric):
    ...     dielectric_coefficient = 4.5
    ...     loss_tangent = 0.02
    >>> class Copper(Conductor):
    ...     roughness = 0.01
    >>> copper1oz = Copper(thickness=0.035)
    >>> class ProjectStackup(Stackup):  # using names
    ...     top_surface = SoldermaskLayer(thickness=0.1)
    ...     top = copper1oz
    ...     inner = FR4(thickness=0.55)
    ...     bottom = copper1oz
    ...     bottom_surface = SoldermaskLayer(thickness=0.1)

    >>> class ProjectStackup2(Stackup):  # or equivalent
    ...     top_surface = Layer(Dielectric(), thickness=0.1)
    ...     layers = [
    ...         Copper(),
    ...         FR4(thickness=0.55),
    ...         Copper(),
    ...     ]
    ...     bottom_surface = Layer(Dielectric(), thickness=0.1)
    """

    name: str | None = None

    __introspecting = False

    @property
    def conductors(self) -> Sequence[Conductor]:
        """The conductors in this stackup."""
        if self.__introspecting:
            # avoid infinite recursion
            return ()
        try:
            self.__introspecting = True
            return RefTuple(decompose(self, Conductor))
        finally:
            self.__introspecting = False


class Symmetric(Stackup):
    """Base class to generate a symmetric stackup. The last layer in the
    stackup will become the innermost dielectric layer in the final result.

    >>> class ProjectStackup(Symmetric):
    ...     outer = Dielectric(thickness=0.1)
    ...     top = Conductor(thickness=0.2)
    ...     core = FR4(thickness=0.55)


    >>> len([layer for layer in decompose(ProjectStackup(), Material)])
    5
    >>> len(ProjectStackup().conductors)
    2
    """

    bottom = None
    """The bottom of the stackup, will be filled in by the stackup generator."""

    def __init__(self):
        super().__init__()
        layers = list(decompose(self, Material))
        if not isinstance(layers.pop(), Dielectric):
            raise TypeError(
                "Last layer must be dielectric to create a symmetric stackup"
            )
        self.bottom = tuple(reversed(layers))

    def __dir__(self):
        # make sure the flipped layers are at the end.
        yield from (field for field in super().__dir__() if field != "bottom")
        yield "bottom"


class Material(Critical):
    """Base class for layer materials. Do not subclass this directly, subclass
    :py:class:`Dielectric` or :py:class:`Conductor` instead. A material
    subclass represents a new material, an instantiated material represents a
    layer of that material in the stackup."""

    material_name: ClassVar[str | None] = None
    """Name of the material. If not specified, the name of the class is used."""
    name: str | None = None
    """Name of the layer. If not specified, the name of the field in the
    stackup is used."""
    thickness: float | None = None
    """Thickness of the layer in mm. Is ideally specified as a class attribute. If
    no thickness is declared for this material, a thickness must be specified
    in the constructor."""

    def __init__(self, *, name: str | None = None, thickness: float | None = None):
        if thickness is not None:
            if self.thickness is not None:
                raise ValueError(
                    "Cannot specify thickness in constructor and as a class attribute"
                )
            self.thickness = thickness
        else:
            if self.thickness is None:
                raise ValueError("Material has no thickness")
        if name is not None:
            self.name = name
        super().__init__()


class Dielectric(Material):
    """A dielectric material. Subclass this to create a new dielectric
    material, setting the dielectric coefficient and loss tangent as
    appropriate as a class attributes. If the name of the class is insufficient to
    identify the material, set the ``material_name`` class attribute as well.

    >>> class FR4(Dielectric):
    ...     "Material description goes in the docstring."
    ...     dielectric_coefficient = 4.4
    ...     loss_tangent = 0.0168

    >>> class FR4Prepreg(FR4):
    ...     thickness = 0.21

    >>> class FR4Core(FR4):
    ...     thickness = 1.065
    """

    dielectric_coefficient: ClassVar[float | None] = None
    loss_tangent: ClassVar[float | None] = None


class Conductor(Material):
    """A conductive material. Subclass this to create a new conductive
    material, setting the roughness as appropriate as a class attribute. If
    the name of the class is insufficient to identify the material, set the
    ``material_name`` class attribute as well.

    >>> class Copper1oz(Conductor):
    ...     "Material description for our 1oz copper goes in the docstring."
    ...     material_name = "Copper 1oz"
    ...     thickness = 0.035
    """

    roughness: ClassVar[float | None] = None


del Critical
