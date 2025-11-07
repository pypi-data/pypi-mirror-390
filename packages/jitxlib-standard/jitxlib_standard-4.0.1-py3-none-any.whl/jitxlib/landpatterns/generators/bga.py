from collections.abc import Iterable

from jitx.anchor import Anchor
from jitx.shapes.primitive import Circle
from jitx.transform import Transform

from ..courtyard import ExcessCourtyard
from ..grid_layout import A1, AlphaDictNumbering, GridLandpatternGenerator, GridPosition
from ..grid_planner import GridPlannerMixin
from ..pads import GridPadShapeGeneratorMixin
from ..silkscreen.labels import ReferenceDesignatorMixin
from ..silkscreen.marker import Pad1Marker
from ..silkscreen.outlines import SilkscreenOutline


class BGABase(
    GridPlannerMixin,
    GridPadShapeGeneratorMixin,
    GridLandpatternGenerator,
):
    """BGA Landpattern Generator Base"""

    def __init__(
        self,
        num_rows: int,
        num_cols: int,
        ball_diameter: float,
        pitch: float | tuple[float, float],
    ):
        super().__init__()
        self._num_rows = num_rows
        self._num_cols = num_cols
        # self.__ball_diameter = ball_diameter
        if not isinstance(pitch, tuple):
            pitch = (pitch, pitch)
        assert len(pitch) == 2, "pitch must be a tuple of two values"

        self.__pitch = pitch
        self.pad_shape(Circle(diameter=ball_diameter))

    def _generate_layout(self) -> Iterable[GridPosition]:
        num_rows = self._num_rows
        num_cols = self._num_cols
        hpitch, vpitch = self.__pitch
        center_row = (num_rows - 1) / 2.0
        center_col = (num_cols - 1) / 2.0

        # TODO: not sure how to handle this, anchoring is useful for creating
        # sub-landpatterns that can be placed relative to an anchor; but I
        # don't know what the anchor point should be. Center of the grid
        # position at the appropriate corner?

        # half_width = pitch * (num_cols - 1) / 2.0
        # half_height = pitch * (num_rows - 1) / 2.0
        # bounds = (-half_width, -half_height, half_width, half_height)
        # center_x, center_y = self._get_anchor().flip().to_point(bounds)

        center_x, center_y = 0, 0
        for r in range(num_rows):
            row_y = (center_row - r) * vpitch + center_y
            for c in range(num_cols):
                x = (c - center_col) * hpitch + center_x
                yield GridPosition(r, c, Transform.translate(x, row_y))


class BGADecorated(
    SilkscreenOutline, Pad1Marker, ReferenceDesignatorMixin, ExcessCourtyard, BGABase
):
    def __base_init__(self):
        super().__base_init__()
        self.pad_1_marker_direction(Anchor.W)


class BGA(A1, AlphaDictNumbering, BGADecorated):
    """BGA Landpattern Generator"""
