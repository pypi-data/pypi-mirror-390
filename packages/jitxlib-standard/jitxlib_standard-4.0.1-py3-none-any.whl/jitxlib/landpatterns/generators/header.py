from collections.abc import Iterable
from typing import override

from jitx.shapes import Shape
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Circle
from jitx.transform import Transform

from .. import LandpatternGenerator
from ..courtyard import ExcessCourtyard
from ..grid_layout import ColumnMajorOrder, GridPosition, LinearNumbering
from ..grid_planner import GridPlannerMixin
from ..ipc import DensityLevelMixin
from ..leads import SMDLead, THLead
from ..pads import GridPadShapeGeneratorMixin, IPCTHPadConfig
from ..silkscreen.outlines import SilkscreenOutline


class HeaderBase(
    ColumnMajorOrder,
    DensityLevelMixin,
    GridPlannerMixin,
    GridPadShapeGeneratorMixin,
    LandpatternGenerator,
):
    """Pin Header Landpattern Generator Base"""

    def __init__(
        self,
        num_leads: int,
        num_rows: int,
        lead: SMDLead | THLead,
        pitch: float | tuple[float, float],
    ):
        super().__init__()
        self.pad_config(IPCTHPadConfig())
        if num_leads <= 0:
            raise ValueError("num_leads must be positive")
        if num_rows <= 0:
            raise ValueError("num_rows must be positive")
        if num_leads % num_rows != 0:
            raise ValueError("num_leads must be a multiple of num_rows")
        self._num_leads = num_leads
        self._num_rows = num_rows
        self._num_cols = num_leads // num_rows
        self.__pitch = pitch
        self.__lead = lead

    @override
    def _pad_shape(self, pos: GridPosition) -> Shape:
        match self.__lead:
            case SMDLead():
                dims = self.__lead.pad_size(self._density_level)
                return rectangle(dims[0], dims[1])
            case THLead():
                return Circle(diameter=self.__lead.width.typ)
            case _:
                raise ValueError("Invalid lead type")

    @override
    def _generate_layout(self) -> Iterable[GridPosition]:
        if isinstance(self.__pitch, tuple):
            hpitch, vpitch = self.__pitch
        else:
            hpitch = self.__pitch
            vpitch = self.__pitch
        x_base = -hpitch * (self._num_cols - 1) / 2.0
        y_base = vpitch * (self._num_rows - 1) / 2.0
        for c in range(self._num_cols):
            col_x = x_base + c * hpitch
            for r in range(self._num_rows):
                row_y = y_base - r * vpitch
                yield GridPosition(r, c, Transform.translate(col_x, row_y))


class HeaderDecorated(SilkscreenOutline, ExcessCourtyard, HeaderBase):
    pass


class Header(LinearNumbering, HeaderDecorated):
    pass
