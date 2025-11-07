from __future__ import annotations
from typing import override, final, Self
from dataclasses import dataclass
from jitx.shapes import Shape
from jitx.shapes.primitive import Circle
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced
from jitx.placement import Kinematic

from .ipc import DensityLevel


@dataclass(kw_only=True)
class PackageBody(Kinematic):
    """Component package body base class

    This class is the representation of the 3D footprint of a component. Do not
    instantiate directly, but use on of the subclasses instead.
    """

    height: Toleranced
    """Height of the package body"""

    @final
    def envelope(self, density_level: DensityLevel) -> Shape:
        """Compute the envelope of the package body

        This method returns the 2D envelope of the package body at the
        given density level.

        Args:
            density_level: density level to compute the envelope for

        Returns:
            The envelope of the package body at the given density level
        """
        shape = self._envelope(density_level)
        if self.transform:
            shape = shape.at(self.transform)
        return shape

    def _envelope(self, density_level: DensityLevel) -> Shape:
        raise NotImplementedError

    @property
    def dims(self) -> tuple[Toleranced, Toleranced]:
        """Get the axis aligned bounding box dimensions of the package body."""
        raise NotImplementedError(f"{self.__class__.__name__}.dims")


@dataclass
class RectanglePackage(PackageBody):
    """Rectangular PackageBody

    This class represents a rectangular prism bounding box. For a cylindrical
    package body, use :py:class:`~CylinderPackage` instead.
    """

    width: Toleranced
    """Width of the package body"""

    length: Toleranced
    """Length of the package body"""

    @override
    def _envelope(self, density_level: DensityLevel):
        width = self.width.typ
        length = self.length.typ
        match density_level:
            case DensityLevel.A:
                width = self.width.max_value
                length = self.length.max_value
            case DensityLevel.C:
                width = self.width.min_value
                length = self.length.min_value
        return rectangle(width, length)

    @property
    def dims(self) -> tuple[Toleranced, Toleranced]:
        return self.width, self.length


@dataclass
class CylinderPackage(PackageBody):
    """Cylindrical PackageBody

    This class represents a cylindrical bounding box. For a rectangular package
    body, use :py:class:`~RectanglePackage` instead.
    """

    diameter: Toleranced
    """Diameter of the package body"""

    @override
    def _envelope(self, density_level: DensityLevel):
        diameter = self.diameter.typ
        match density_level:
            case DensityLevel.A:
                diameter = self.diameter.max_value
            case DensityLevel.C:
                diameter = self.diameter.min_value
        return Circle(diameter=diameter)

    @property
    def dims(self) -> tuple[Toleranced, Toleranced]:
        return self.diameter, self.diameter


class PackageBodyMixin:
    """Mixin class for components that have a package body"""

    __package_body: PackageBody | None = None
    """Package body of the component"""

    def package_body(self, body: PackageBody) -> Self:
        """Set the package body of the component"""
        self.__package_body = body
        return self

    @property
    def _package_body_optional(self) -> PackageBody | None:
        """Get the package body of the component"""
        return self.__package_body

    def _package_body(self) -> PackageBody:
        """Get the package body of the component"""
        if self.__package_body is None:
            raise RuntimeError("Package body not set")
        return self.__package_body
