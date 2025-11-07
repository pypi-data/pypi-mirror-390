from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import override

from jitx.shapes.primitive import Circle
from jitx.toleranced import Toleranced
from jitx.transform import Transform

from .. import LandpatternGenerator
from ..courtyard import ExcessCourtyard, OriginMarkerMixin
from ..grid_layout import GridPosition, LinearNumbering
from ..leads import THLead
from ..package import PackageBody, PackageBodyMixin
from ..pads import GridPadShapeGeneratorMixin, IPCTHPadConfig
from ..silkscreen.marker import Pad1Marker
from .smt import CathodeAnodeNumbering


# Default lead bend start is 1.0mm from the edge of the package body.
DEFAULT_BEND_START = 1.0


@dataclass(frozen=True)
class THWeldBeadLead(THLead):
    """Through-hole lead with optional weld bead

    This class is used to specify a through-hole lead with an optional weld
    bead. The weld bead is specified as an offset from the lead's center.
    """

    weld_offset: Toleranced = Toleranced.exact(0.0)
    """Weld bead offset

    Additional margin to provide around a lead to account for the weld bead.
    """


class AxialMounting(Enum):
    """Axial component mounting style

    This enum is used to specify the mounting style of an axial component.
    """

    Horizontal = "Horizontal"
    """Horizontal Mounting Style

    This is the typical mounting style where the lead axis is parallel to the
    board surface.
    """

    Vertical = "Vertical"
    """Vertical Mounting Style

    This is the mounting style where the lead axis is perpendicular to the board
    surface, and the lead pointing away from the board surface is bent 180
    degrees to return to the board surface.
    """


def compute_default_bend_radius(lead_diameter: Toleranced) -> float:
    """Compute default target bend radius.

    .. seealso::

        IPC-A-610 Section 7.1.2, Table 7-1 Lead Bend Radius
    """
    diam = lead_diameter.typ
    if diam < 0.8:
        return diam
    elif diam < 1.2:
        return 1.5 * diam
    else:
        return 2.0 * diam


@dataclass(frozen=True)
class LeadBend:
    radius: float
    """Radius of the bend in the lead"""
    start: float = 1.0
    """Lead bend start from the edge of the package body. Default is 1.0mm."""


DEFAULT_BEND_START = 1.0


class AxialTwoPinBase(
    PackageBodyMixin, GridPadShapeGeneratorMixin, LandpatternGenerator
):
    _num_rows = 2
    _num_cols = 1

    def __init__(
        self,
        *,
        lead: THLead,
        package_body: PackageBody,
        mounting: AxialMounting = AxialMounting.Horizontal,
        bend: LeadBend | None = None,
    ):
        super().__init__()
        self.__lead = lead
        self.__mounting = mounting

        self.pad_config(IPCTHPadConfig())
        self.package_body(package_body)

        if isinstance(lead, THWeldBeadLead):
            self.__weld_offset = lead.weld_offset.typ
        else:
            self.__weld_offset = 0.0

        if bend is not None:
            self.__bend = bend
        else:
            self.__bend = LeadBend(compute_default_bend_radius(lead.width))

    def __lead_spacing(self) -> float:
        lead = self.__lead
        package_body = self._package_body()
        mounting = self.__mounting
        weld_offset = self.__weld_offset
        bend_radius = self.__bend.radius
        bend_start = self.__bend.start
        width, length = package_body.dims

        match mounting:
            case AxialMounting.Horizontal:
                base_len = length.typ
                bend_len = bend_radius + bend_start + weld_offset
                return base_len + 2.0 * bend_len
            case AxialMounting.Vertical:
                body_radius = width.typ / 2.0
                lead_radius = lead.width.typ / 2.0
                # TODO - explain margin magic number
                bend_diam = body_radius + lead_radius + 0.1
                bend_len = bend_radius + bend_start
                # Take the max of the computed radius and the minimum bend
                # radius
                return max(bend_diam / 2.0, bend_radius)

    @override
    def _generate_layout(self) -> Iterable[GridPosition]:
        half_spacing = self.__lead_spacing() / 2.0
        return (
            GridPosition(0, 0, Transform.translate(0.0, half_spacing)),
            GridPosition(1, 0, Transform.translate(0.0, -half_spacing)),
        )

    @override
    def _pad_shape(self, pos: GridPosition):
        return Circle(diameter=self.__lead.width.typ)


class AxialTwoPinDecorated(OriginMarkerMixin, ExcessCourtyard, AxialTwoPinBase):
    pass


class PolarizedAxialTwoPin(CathodeAnodeNumbering, Pad1Marker, AxialTwoPinDecorated):
    pass


class AxialTwoPin(LinearNumbering, AxialTwoPinDecorated):
    pass
