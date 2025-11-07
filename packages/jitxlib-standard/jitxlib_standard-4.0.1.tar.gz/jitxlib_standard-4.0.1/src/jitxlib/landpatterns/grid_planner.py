from __future__ import annotations
from collections.abc import Callable
from typing import Self, override

from jitx.transform import IDENTITY

from .grid_layout import GridLayoutInterface, GridPosition


class GridPlanner:
    """Grid Planner Class

    This base class provides an interface for determining which pads in a grid
    are active. Each subclass defines a 'pattern' of grid locations which are
    inactive or active. These can be composed together to create more complex
    grid patterns.
    """

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool | None:
        """Determine if a pad is active based on the row and column.

        Args:
            pos: The grid location to check.
            num_rows: The total number of rows in the grid.
            num_cols: The total number of columns in the grid.

        Returns:
            True if the pad is active, False if the pad is inactive. Returns
            None if this planner does not specify whether this pad is active
            or inactive (the decision is deferred to the next planner in the
            composition). If all planners return None for a pad, the pad
            is considered active by default.
        """

        # Default is planner is a full grid
        return True

    def num_active(self, num_rows: int, num_cols: int) -> int:
        """Convenience helper function to determine the number of active pads in the grid."""
        return sum(
            1
            for row in range(num_rows)
            for col in range(num_cols)
            if self.is_active(GridPosition(row, col, IDENTITY), num_rows, num_cols)
            is not False
        )


class GridPlannerMixin(GridLayoutInterface):
    __grid_planner: GridPlanner | None = None
    __grid_planner_fn: Callable[[GridPosition, int, int], bool] | None = None

    def grid_planner(
        self, grid_planner: GridPlanner | Callable[[GridPosition, int, int], bool]
    ) -> Self:
        if isinstance(grid_planner, Callable):
            self.__grid_planner = None
            self.__grid_planner_fn = grid_planner
        else:
            self.__grid_planner = grid_planner
            self.__grid_planner_fn = None
        return self

    @override
    def _active_pad(self, pos: GridPosition) -> bool:
        if self.__grid_planner is None:
            if self.__grid_planner_fn is None:
                return True
            return self.__grid_planner_fn(pos, self._num_rows, self._num_cols)
        active = self.__grid_planner.is_active(pos, self._num_rows, self._num_cols)
        if active is None:
            return True
        return active


class CompositeGridPlanner(GridPlanner):
    """Composite Grid Planner

    This planner is a composite of other planners. For a given pad, the first
    planner that returns a non-None result is used. If all planners return
    None then None is returned. This allows more complex grid patterns to be
    created by composing multiple planners together.
    """

    def __init__(self, *planners: GridPlanner):
        """Initialize the composite grid planner

        Args:
            planners: The planners to compose together, in order of priority.
                Earlier planners take precedence over later planners.
        """
        self.planners = list(planners)

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool | None:
        for planner in self.planners:
            result = planner.is_active(pos, num_rows, num_cols)
            if result is not None:
                return result
        return None


class StaggeredGridPlanner(GridPlanner):
    """Staggered Grid Planner

    This planner creates a grid where every other pad is inactive. The parity
    can be flipped by changing the ``top_left_active`` parameter.
    """

    def __init__(self, *, top_left_active: bool = True):
        """Initialize the staggered grid planner

        Args:
            top_left_active: whether the top-left pad is active.
        """
        self.top_left_active = top_left_active

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool | None:
        row = pos.row
        col = pos.column
        return (row + col) % 2 == (0 if self.top_left_active else 1)


class PerimeterGridPlanner(GridPlanner):
    """Perimeter Grid Planner

    This planner creates a grid where only the pads on the perimeter are active.
    The width of the perimeter can be controlled by the ``perimeter_width``
    parameter.
    """

    def __init__(self, perimeter_width: int):
        """Initialize the perimeter grid planner

        Args:
            perimeter_width: The width of the perimeter to keep in number of
                rows/columns. The width is measured from the edge of the grid.
        """
        assert perimeter_width >= 0
        self.perimeter_width = perimeter_width

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool:
        row = pos.row
        col = pos.column
        return not (
            self.perimeter_width <= row < num_rows - self.perimeter_width
            and self.perimeter_width <= col < num_cols - self.perimeter_width
        )


class IslandGridPlanner(GridPlanner):
    """Island Grid Planner

    This planner creates a rectangular region of pads that are either active or
    inactive. The indices are one-indexed and inclusive (both start and end
    indices are included). Rows go from top to bottom, columns from left to
    right. Negative indices are allowed, and indicate counting from the other
    side (i.e. -1 is the bottom row or rightmost column). 0 is not a valid
    index. The planner returns ``None`` for pads that are not in the island.
    """

    def __init__(
        self,
        row_start: int,
        row_end: int,
        col_start: int,
        col_end: int,
        *,
        active: bool = False,
    ):
        """Initialize the island grid planner

        Args:
            row_start: starting row of the island, 1-indexed and inclusive.
            row_end: ending row of the island, 1-indexed and inclusive.
            col_start: starting column of the island, 1-indexed and inclusive.
            col_end: ending column of the island, 1-indexed and inclusive.
            active: whether the island is active or inactive.
                Default is inactive.
        """
        assert row_start != 0, f"{row_start} is not a valid index"
        assert row_end != 0, f"{row_end} is not a valid index"
        assert col_start != 0, f"{col_start} is not a valid index"
        assert col_end != 0, f"{col_end} is not a valid index"

        self.row_start = row_start
        self.row_end = row_end
        self.col_start = col_start
        self.col_end = col_end
        self.active = active

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool | None:
        row = pos.row
        col = pos.column
        row = row + 1  # zero-indexed to one-indexed
        col = col + 1  # zero-indexed to one-indexed

        def wrap(index: int, mod: int) -> int:
            if index > 0:
                return index
            else:
                return index + mod + 1

        rs = wrap(self.row_start, num_rows)
        re = wrap(self.row_end, num_rows)
        cs = wrap(self.col_start, num_cols)
        ce = wrap(self.col_end, num_cols)
        if row >= rs and row <= re and col >= cs and col <= ce:
            return self.active
        return None


def InactiveIslandGridPlanner(
    row_start: int, row_end: int, col_start: int, col_end: int
) -> IslandGridPlanner:
    """Create an inactive island grid planner

    Args:
        row_start: starting row of the island, 1-indexed and inclusive.
        row_end: ending row of the island, 1-indexed and inclusive.
        col_start: starting column of the island, 1-indexed and inclusive.
        col_end: ending column of the island, 1-indexed and inclusive.

    Returns:
        An inactive island grid planner
    """
    return IslandGridPlanner(row_start, row_end, col_start, col_end, active=False)


def ActiveIslandGridPlanner(
    row_start: int, row_end: int, col_start: int, col_end: int
) -> IslandGridPlanner:
    """Create an active island grid planner

    Args:
        row_start: starting row of the island, 1-indexed and inclusive.
        row_end: ending row of the island, 1-indexed and inclusive.
        col_start: starting column of the island, 1-indexed and inclusive.
        col_end: ending column of the island, 1-indexed and inclusive.

    Returns:
        An active island grid planner
    """
    return IslandGridPlanner(row_start, row_end, col_start, col_end, active=True)


class CornerCutGridPlanner(GridPlanner):
    """Corner Cut Grid Planner

    This planner creates a grid where the pads in the triangles at the corners
    of the grid are inactive. The width (the "legs" of the right triangle)
    of the triangles is controlled by the ``corner_width`` parameter.
    """

    def __init__(self, corner_width: int):
        """Initialize the corner cut grid planner

        Args:
            corner_width: The width of the corner triangles to be left inactive.
        """
        assert corner_width >= 0
        self.corner_width = corner_width

    def is_active(self, pos: GridPosition, num_rows: int, num_cols: int) -> bool | None:
        row = pos.row
        col = pos.column
        vgap = min(row, num_rows - row - 1)
        hgap = min(col, num_cols - col - 1)
        if vgap + hgap < self.corner_width:
            return False
        else:
            return None
