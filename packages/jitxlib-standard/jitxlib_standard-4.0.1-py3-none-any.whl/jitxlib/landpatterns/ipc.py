from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Literal, Self
import math

from jitx.context import Context
from jitx.toleranced import Toleranced
from jitx._structural import Structurable

if TYPE_CHECKING:
    from .leads.fillets import LeadFillets


class DensityLevel(Enum):
    """Density Level

    This enum specifies the density level for footprints on a PCB. Higher
    density levels indicate less space between landpatterns. These are defined
    in IPC-7351.
    """

    A = "A"
    """Density Level A

    Maximum land protrusion
    """

    B = "B"
    """Density Level B

    Median (nominal) land protrusion
    """

    C = "C"
    """Density Level C

    Minimum land protrusion
    """


@dataclass
class IPCRequirements:
    """IPC Formula Results from Section 3 of IPC 7351B

    This class contains the results of the IPC formula for computing the pad
    size.

    TODO: Add Diagram here
    """

    Zmax: float
    """Maximum overall length"""

    Gmin: float
    """Minimum distance between pads"""

    Xmin: float
    """Minimum pad width"""

    def pad_size(self) -> tuple[float, float]:
        """Compute the pad dimensions from this IPC result

        Returns:
            The pad dimensions as (y, x)"""
        return (0.5 * (self.Zmax - self.Gmin), self.Xmin)


def compute_ipc(
    leadSpan: Toleranced,
    leadLength: Toleranced,
    leadWidth: Toleranced,
    fillets: LeadFillets,
) -> IPCRequirements:
    """Compute Pad Geometry According to IPC Rules

    Args:
        leadSpan: edge-of-lead to edge-of-lead distance for an IC package.
        leadLength: length of the exposed contact in the same dimension as `leadSpan`
        leadWidth: width of the exposed contact in the dimension orthogonal to `leadSpan`
        fillets: Specifications for the solder fillets created when soldering the
            lead to the land-pattern pad. These parameters define extra spacing around the lead
            dimension to form these fillets.

    Returns:
        IPCResult containing the results of the IPC formula
    """
    Jt = fillets.toe
    Jh = fillets.heel
    Js = fillets.side

    Lmax = leadSpan.max_value
    Lmin = leadSpan.min_value
    Wmin = leadWidth.min_value
    Tmin = leadLength.min_value
    Smax = Lmax - 2.0 * Tmin
    C_L = leadSpan.range()
    C_W = leadWidth.range()
    C_T = leadLength.range()
    C_S = math.sqrt(C_L * C_L + C_T * C_T)
    # the distance from edge of land to edge of land on the exterior of the land pattern
    Zmax = Lmin + 2.0 * Jt + C_L
    # the distance from edge of land to edge of land on the interior of the land pattern
    Gmin = Smax - 2.0 * Jh - C_S
    # the size of the land in the dimension orthogonal to Z and G.
    Xmin = Wmin + 2.0 * Js + C_W
    return IPCRequirements(Zmax, Gmin, Xmin)


@dataclass(frozen=True)
class DensityLevelContext(Context):
    _global_default: ClassVar[DensityLevelContext]
    density_level: DensityLevel

    @classmethod
    def get(cls) -> DensityLevelContext:
        # do not construct a new object here, it'll taint caching mechanisms.
        return super().get() or DensityLevelContext._global_default


DensityLevelContext._global_default = DensityLevelContext(DensityLevel.C)


# make use of contexts, so much be instantiated in context.
class DensityLevelMixin(Structurable):
    __density_level: DensityLevel | None = None
    __density_level_ctx: DensityLevel

    if not TYPE_CHECKING:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__density_level_ctx = DensityLevelContext.get().density_level

    def density_level(
        self, density_level: DensityLevel | Literal["A"] | Literal["B"] | Literal["C"]
    ) -> Self:
        if isinstance(density_level, str):
            density_level = DensityLevel[density_level]
        self.__density_level = density_level
        return self

    @property
    def _density_level(self) -> DensityLevel:
        return self.__density_level or self.__density_level_ctx
