from __future__ import annotations
from typing import Self, overload, override
from collections.abc import Iterable, Sequence

from jitx.shapes import Shape
from jitx.shapes.composites import rectangle
from jitx.transform import Transform

from .leads import LeadProfileMixin

from .ipc import DensityLevelMixin
from .grid_layout import (
    ColumnMajorOrder,
    GridLandpatternGenerator,
    GridLayout,
    GridPosition,
)
from .pads import GridPadShapeGeneratorMixin, PadShapeProvider


def _twoway[T](seq: Sequence[T]) -> tuple[T, T]:
    if len(seq) == 2:
        return seq[0], seq[1]
    elif len(seq) == 1:
        return seq[0], seq[0]
    raise ValueError("Sequence must be of length 2 or 1")


def _fourway[T](seq: Sequence[T]) -> tuple[T, T, T, T]:
    if len(seq) == 4:
        return seq[0], seq[1], seq[2], seq[3]
    elif len(seq) == 2:
        return seq[0], seq[1], seq[0], seq[1]
    elif len(seq) == 1:
        return seq[0], seq[0], seq[0], seq[0]
    raise ValueError("Sequence must be of length 4, 2, or 1")


class QuadColumnLeadShape(
    LeadProfileMixin,
    DensityLevelMixin,
    GridPadShapeGeneratorMixin,
):
    @override
    def _pad_shape(self, pos: GridPosition) -> Shape:
        profiles = self._lead_profiles()
        if profiles is None:
            return super()._pad_shape(pos)
        ps = _twoway(profiles)
        w, h = ps[pos.column & 1].compute_placements(self._density_level).pad_size
        return self._pad_rectangle(w, h)

    def _pad_rectangle(self, width: float, height: float) -> Shape:
        return rectangle(width, height)


class QuadColumn(
    ColumnMajorOrder,
    QuadColumnLeadShape,
    GridLandpatternGenerator,
):
    """Quad Column Pad Grid Generator

    This class constructs the pad grid for a quad column package often refered
    to as a quad package such as a QFN, QFP, etc.

    The idea is that the grid gets constructed in a way that is conducive
    for making the landpattern.

    The idea is that this constructs a 4-Column grid where:
    1.  Column 0 is in `-X` half plane and orders ascending for +Y to -Y
    2.  Column 1 is in the `-Y` half-plane and is rotated 90 degrees
    3.  Column 2 is in the `+X` half plane and is rotated 180 degrees
    4.  Column 3 is in the `+Y` half-plane and is rotated 270 degrees

    This creates the typical numbering scheme for ICs:

    .. code-block:: text

        Left-Row  Col 0               Col 2    Right-Row
            Col 3 ->  16 15 14 13
        0          1               12         3
        1          2               11         2
        2          3               10         1
        3          4               9          0
            Col 1 ->  5  6  7  8

    The naming of the pads is done by a numbering scheme that must also be
    mixed in to the subclass.
    """

    _leads_per_column: tuple[int, int, int, int]

    @overload
    def __init__(
        self, num_rows: int | tuple[int] | tuple[int, int] | tuple[int, int, int, int]
    ): ...
    @overload
    def __init__(self, *, num_leads: int): ...
    def __init__(
        self,
        num_rows: int
        | tuple[int]
        | tuple[int, int]
        | tuple[int, int, int, int]
        | None = None,
        *,
        num_leads: int | None = None,
    ):
        super().__init__()
        if isinstance(num_leads, int):
            if num_leads % 4 != 0:
                raise ValueError("num_leads must be a multiple of 4")
            num_rows = num_leads // 4
        if isinstance(num_rows, int):
            num_rows = (num_rows,)
        if num_rows is None:
            raise ValueError("Either num_rows or num_leads must be specified")
        self._leads_per_column = _fourway(num_rows)
        self._num_rows = max(*self._leads_per_column)
        self._num_cols = 4

    @override
    def _generate_layout(self) -> Iterable[GridPosition]:
        placements = _twoway(self._lead_placements())
        anchor_tx = Transform.identity()
        # half_width = placements[0].center / 2.0
        # half_height = placements[1].center / 2.0
        # anchor_tx = Transform.translate(
        #     self.get_anchor()
        #     .flip()
        #     .to_point((-half_width, -half_height, half_width, half_height))
        # )
        for c in range(self._num_cols):
            placement = placements[c & 1]
            x_dist = placement.center / 2.0
            pitch = placement.pitch
            rot = 90.0 * c
            offset = Transform.rotate(rot) * Transform.translate(-x_dist, 0.0)
            num_rows = self._leads_per_column[c & 3]
            center_row = (num_rows - 1) / 2.0
            for r in range(num_rows):
                y = (center_row - r) * pitch
                tx = anchor_tx * offset * Transform.translate(0.0, y)
                yield GridPosition(r, c, tx)


class CornerPadChamfer(PadShapeProvider, GridLayout):
    __chamfer: float | None = None

    def corner_pad_chamfer(self, radius: float) -> Self:
        """Chamfer the corners of the pads"""
        self.__chamfer = radius
        return self

    @override
    def _pad_shape(self, pos: GridPosition) -> Shape:
        shape = super()._pad_shape(pos)
        if isinstance(self, QuadColumn):
            num_rows = self._leads_per_column[pos.column]
        else:
            num_rows = self._num_rows
        if self.__chamfer and pos.row in (0, num_rows - 1):
            lox, loy, hix, hiy = shape.to_shapely().bounds
            w = hix - lox
            h = hiy - loy
            mid = (hix + lox) / 2, (hiy + loy) / 2

            radius = self.__chamfer

            if pos.row:
                # bottom of row, chamfer bottom right corner
                shape = rectangle(w, h, chamfer=(0, 0, 0, radius)).at(mid)
            else:
                # top of row, chamfer top right corner
                shape = rectangle(w, h, chamfer=(radius, 0, 0, 0)).at(mid)

            # TODO, if the pad shape is not a rectangle, we should intersect
            # the chamfer shape with the pad shape.
        return shape
