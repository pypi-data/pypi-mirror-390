from typing import overload
from collections.abc import Iterable, Sequence

from jitx.shapes import Shape
from jitx.shapes.composites import rectangle
from jitx.transform import Transform

from .grid_layout import GridPosition, GridLandpatternGenerator, ColumnMajorOrder
from .pads import GridPadShapeGeneratorMixin
from .leads import LeadProfileMixin


class DualColumnLeadShape(LeadProfileMixin, GridPadShapeGeneratorMixin):
    def _pad_shape(self, pos: GridPosition) -> Shape:
        profiles = self._lead_profiles_optional
        if profiles is None:
            return super()._pad_shape(pos)
        p = _oneway(profiles)
        w, h = p.compute_placements(self._density_level).pad_size
        return self._pad_rectangle(w, h)

    def _pad_rectangle(self, width: float, height: float) -> Shape:
        return rectangle(width, height)


def _oneway[T](seq: Sequence[T]) -> T:
    return seq[0]


class DualColumn(
    ColumnMajorOrder,
    DualColumnLeadShape,
    GridLandpatternGenerator,
):
    """Dual Column Pad Generator

    This class constructs the pad grid for dual column (otherwise called dual
    row) component such as a SOIC or SOP.

    The idea is that the grid gets constructed in a way that is conducive
    for making the landpattern. For example:

    .. code-block:: text

        Left-Row    Col 0   Col 1   Right-Row
          0          1       8         3
          1          2       7         2
          2          3       6         1
          3          4       5         0

    Notice how Column 1 is rotated 180 degrees relative to Column 0.
    """

    _num_cols = 2

    @overload
    def __init__(self, *, num_rows: int): ...
    @overload
    def __init__(self, *, num_leads: int): ...

    def __init__(self, *, num_rows: int | None = None, num_leads: int | None = None):
        super().__init__()

        if num_rows is not None:
            self._num_rows = num_rows
        elif num_leads is not None:
            if num_leads % 2 != 0:
                raise ValueError("num_leads must be a multiple of 2")
            self._num_rows = num_leads // 2
        else:
            raise ValueError("Either num_rows or num_leads must be specified")

    def _generate_layout(self) -> Iterable[GridPosition]:
        placement = _oneway(self._lead_placements())

        for c in range(self._num_cols):
            # For column 0 (negative X half-plane) - no rotation applied
            #  This places pads 1-> N/2 in ascending order.
            # For column 1 (positive X half-plane) - 180 rotation applied
            #   This places pads (N/2 + 1) -> N in descending order
            rot = 180.0 * c
            offset = Transform.rotate(rot) * Transform.translate(
                -placement.center / 2.0, 0.0
            )
            num_rows = self._num_rows
            center_row = (num_rows - 1) / 2.0
            for r in range(num_rows):
                y = (center_row - r) * placement.pitch
                tx = offset * Transform.translate(0.0, y)
                yield GridPosition(r, c, tx)
