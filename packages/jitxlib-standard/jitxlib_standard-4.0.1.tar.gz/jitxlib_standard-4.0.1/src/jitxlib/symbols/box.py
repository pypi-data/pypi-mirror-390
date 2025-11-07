"""
Box symbol module for JITX Standard Library

This module provides box symbol definitions for creating rectangular symbols
with configurable pin layouts and spacing.

Quick Start:
    >>> # Auto-generated symbol
    >>> class MyComponent(Component):
    ...     GND = Port()
    ...     VCC = Port()
    ...     IN = [Port() for _ in range(3)]
    ...     OUT = [Port() for _ in range(5)]
    ...     symbol = BoxSymbol()

    >>> # Custom layout
    >>> class MyComponent(Component):
    ...     GND = Port()
    ...     VCC = Port()
    ...     IN = [Port() for _ in range(3)]
    ...     OUT = [Port() for _ in range(5)]
    ...     symbol = BoxSymbol(
    ...         rows=[
    ...             Row(left=PinGroup(IN), right=PinGroup(OUT)),
    ...         ],
    ...         columns=[
    ...             Column(up=PinGroup(VCC), down=PinGroup(GND)),
    ...         ],
    ...     )
"""

from __future__ import annotations
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from functools import reduce
import math
import re

from jitx._structural import Container, Structurable, pathstring
from jitx.component import CurrentComponent
from jitx.shapes import Shape
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Polyline
from jitx.symbol import Direction, Pin, SymbolMapping
from jitx.transform import Transform
from jitx.net import Port
from jitx.inspect import extract, visit

from .common import DEF_PAD_NAME_SIZE, DEF_PIN_LENGTH, DEF_PIN_NAME_SIZE
from .decorators import PinDecorator, DecoratorPlacement, draw, placement
from .label import LabelConfigurable, LabelledSymbol


class SpaceType(Enum):
    """Types of spaces in box symbol layout"""

    CORNER = "corner"  # Corner margin space
    ROW_COL_SPACING = "row_col_spacing"  # Space between rows or cols
    ROW_COL_SPACING_ALIGN = "row_col_spacing_align"  # Space between rows or cols, aligned to the larger of the two
    GROUP_SPACING = "group_spacing"  # Space between pin groups within a row or col
    PIN_SPACING = "pin_spacing"  # Space between pins within a group
    PRE_PIN_SPACING = "pre_pin_spacing"  # Space before pins enlarged by decorators


@dataclass
class SpaceEntry:
    """Entry describing a space in the box symbol layout"""

    value: float
    type: SpaceType


# Box specific constants
DEF_MIN_WIDTH = 2.0
DEF_MIN_HEIGHT = 2.0
DEF_PIN_SPACING = 2.0
DEF_CORNER_MARGIN = 2.0
DEF_GROUP_SPACING = 2.0
DEF_ROW_SPACING = 2.0
DEF_COLUMN_SPACING = 2.0


class PinGroup(Structurable):
    """A group of pins with optional positioning and margins.

    >>> # Group of input pins
    >>> IN = [Port() for _ in range(3)]
    >>> input_group = PinGroup(IN)
    """

    pins: Sequence[Port]

    def __init__(
        self,
        pins: Iterable[Port] | Port,
        *args: Port,
        pre_margin: float | None = None,
        post_margin: float | None = None,
    ):
        """
        Create a PinGroup with pins and optional margins.

        Args:
            pins: Individual Port or an iterable of Ports
            *args: Additional individual Port arguments
            pre_margin: Margin above this group for groups in a row, or to the left
                       of this group for groups in a column (uses group_spacing if None)
            post_margin: Margin below this group for groups in a row, or to the right
                        of this group for groups in a column (uses group_spacing if None)
        """
        if not isinstance(pins, Iterable):
            pins = (pins,)
        else:
            pins = tuple(pins)
        self.pins = pins + args
        self.pre_margin = pre_margin
        self.post_margin = post_margin

        spread_pins = []
        for pin in self.pins:
            if pin.is_single_pin():
                spread_pins.append(pin)
            else:
                for port in extract(pin, Port):
                    if port.is_single_pin():
                        spread_pins.append(port)
        self.pins = tuple(spread_pins)

        # Validation
        if not self.pins:
            raise ValueError("PinGroup must have at least one pin")
        if self.pre_margin and self.pre_margin < 0:
            raise ValueError("PinGroup pre_margin must be non-negative if provided")
        if self.post_margin and self.post_margin < 0:
            raise ValueError("PinGroup post_margin must be non-negative if provided")


class Row(Structurable):
    """A row in the box symbol grid, containing Left and Right pin groups.

    Rows define horizontal arrangements of pins. Pins on the left extend outward
    to the left, and pins on the right extend outward to the right. Pins are arranged
    in the order they are given, from top to bottom.

    >>> # Single row with inputs on left, outputs on right
    >>> row = Row(
    ...     left=PinGroup(IN),
    ...     right=PinGroup(OUT)
    ... )
    """

    left: Sequence[PinGroup]
    right: Sequence[PinGroup]
    top_margin: float | None
    bottom_margin: float | None

    def __init__(
        self,
        left: Iterable[PinGroup] | PinGroup = (),
        right: Iterable[PinGroup] | PinGroup = (),
        top_margin: float | None = None,
        bottom_margin: float | None = None,
    ):
        """
        Create a Row with pin groups and optional margins.

        Args:
            left: Individual PinGroup or an iterable of PinGroups for the Left direction
            right: Individual PinGroup or an iterable of PinGroups for the Right direction
            top_margin: Margin above this row (uses row_spacing if None)
            bottom_margin: Margin below this row (uses row_spacing if None)
        """
        if isinstance(left, PinGroup):
            left = (left,)
        else:
            left = tuple(left)

        if isinstance(right, PinGroup):
            right = (right,)
        else:
            right = tuple(right)

        self.left = left
        self.right = right
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin

        # Validation
        if self.top_margin is not None and self.top_margin < 0:
            raise ValueError("Row top_margin must be non-negative if provided")
        if self.bottom_margin is not None and self.bottom_margin < 0:
            raise ValueError("Row bottom_margin must be non-negative if provided")


class Column(Structurable):
    """A column in the box symbol grid, containing Up and Down pin groups.

    Columns define vertical arrangements of pins. Pins on top extend upward,
    and pins on bottom extend downward. Pins are arranged in the order they are given,
    from left to right.

    >>> # Column with power pins on top, ground on bottom
    >>> col = Column(
    ...     up=PinGroup(VCC, VREF),
    ...     down=PinGroup(GND)
    ... )
    """

    up: Sequence[PinGroup]
    down: Sequence[PinGroup]
    left_margin: float | None
    right_margin: float | None

    def __init__(
        self,
        up: Iterable[PinGroup] | PinGroup = (),
        down: Iterable[PinGroup] | PinGroup = (),
        left_margin: float | None = None,
        right_margin: float | None = None,
    ):
        """
        Create a Column with pin groups and optional margins.

        Args:
            up: Individual PinGroup or an iterable of PinGroups for the Up direction
            down: Individual PinGroup or an iterable of PinGroups for the Down direction
            left_margin: Margin to the left of this column (uses col_spacing if None)
            right_margin: Margin to the right of this column (uses col_spacing if None)
        """
        if isinstance(up, PinGroup):
            up = (up,)
        else:
            up = tuple(up)

        if isinstance(down, PinGroup):
            down = (down,)
        else:
            down = tuple(down)

        self.up = up
        self.down = down
        self.left_margin = left_margin
        self.right_margin = right_margin

        # Validation
        if self.left_margin is not None and self.left_margin < 0:
            raise ValueError("Column left_margin must be non-negative if provided")
        if self.right_margin is not None and self.right_margin < 0:
            raise ValueError("Column right_margin must be non-negative if provided")


@dataclass
class BoxConfig(LabelConfigurable):
    """Configuration for box symbols.

    Controls spacing, sizing, and text appearance for box-style schematic symbols.
    Can be set on a box symbol or globally via SymbolStyleContext.

    >>> # Custom configuration for a compact symbol
    >>> config = BoxConfig(
    ...     pin_spacing=1.0,
    ...     corner_margin=1.0,
    ...     group_spacing=1.0,
    ... )
    >>> symbol = BoxSymbol(rows=rows, columns=columns, config=config)
    """

    min_width: float = DEF_MIN_WIDTH
    """Minimum width of the box, required to be at least 2"""
    min_height: float = DEF_MIN_HEIGHT
    """Minimum height of the box, required to be at least 2"""
    pin_spacing: float = DEF_PIN_SPACING
    """Spacing between pins within the same group, required to be at least 1"""
    corner_margin: float = DEF_CORNER_MARGIN
    """Margin from box corners to first/last pins, required to be at least 1"""
    group_spacing: float = DEF_GROUP_SPACING
    """Spacing between pin groups on the same side, required to be at least 1"""
    row_spacing: float = DEF_ROW_SPACING
    """Spacing between rows in grid layout"""
    col_spacing: float = DEF_COLUMN_SPACING
    """Spacing between columns in grid layout"""
    pin_length: int = DEF_PIN_LENGTH
    """Length of the pin"""
    pin_name_size: float | None = DEF_PIN_NAME_SIZE
    """Size of the pin name text"""
    pad_name_size: float | None = DEF_PAD_NAME_SIZE
    """Size of the pad name text"""

    def __post_init__(self):
        if self.min_width < 2:
            raise ValueError("Box symbol config min_width must be at least 2")
        if self.min_height < 2:
            raise ValueError("Box symbol config min_height must be at least 2")
        if self.pin_spacing < 1:
            raise ValueError("Box symbol config pin_spacing must be at least 1")
        if self.corner_margin < 1:
            raise ValueError("Box symbol config corner_margin must be at least 1")
        if self.group_spacing < 1:
            raise ValueError("Box symbol config group_spacing must be at least 1")
        if self.row_spacing < 0:
            raise ValueError("Box symbol config row_spacing must be non-negative")
        if self.col_spacing < 0:
            raise ValueError("Box symbol config col_spacing must be non-negative")
        if self.pin_length < 0:
            raise ValueError("Box symbol config pin_length must be non-negative")
        if self.pin_name_size is not None and self.pin_name_size < 0:
            raise ValueError("Box symbol config pin_name_size must be non-negative")
        if self.pad_name_size is not None and self.pad_name_size < 0:
            raise ValueError("Box symbol config pad_name_size must be non-negative")


class SymbolBox(LabelledSymbol):
    """Box-shaped symbol"""

    _config: BoxConfig
    box: Shape
    p: tuple[Pin, ...]
    decorators: tuple[tuple[Shape, ...], ...]
    _debug_grid: tuple[Polyline, ...]

    def __init__(self, config: BoxConfig):
        self._config = config
        self.pin_name_size = config.pin_name_size
        self.pad_name_size = config.pad_name_size

    @property
    def config(self) -> BoxConfig:
        """Configuration object that provides label configuration"""
        return self._config

    @property
    def label_config(self) -> BoxConfig:
        return self.config

    def set_pins(self, pins: Sequence[Pin]):
        # Pin name doesn't particularly matter here, because a component port will be assigned to this symbol pin.
        # The visualizer will display the port name, not the pin name.
        # `p` is chosen here as a base name.
        self.p = tuple(pins)


class BoxSymbol(Container):
    """Container for a box-shaped symbol with pins, artwork, labels, and a symbol mapping.

    BoxSymbol creates rectangular schematic symbols with pins on all four sides.
    Pins are organized into Rows of left and right pins and Columns of up and down pins.
    If no rows/columns are provided, the symbol auto-generates from component ports.

    Examples:
        >>> # Auto-generated symbol from component ports
        >>> class MyComponent(Component):
        ...     IN = [Port() for _ in range(4)]
        ...     OUT = [Port() for _ in range(4)]
        ...     VCC = Port()
        ...     GND = Port()
        ...
        ...     def __init__(self):
        ...         self.symbol = BoxSymbol()  # Auto-arranges all ports

        >>> # Manual layout with rows and columns
        >>> class MyComponent(Component):
        ...     IN = [Port() for _ in range(8)]
        ...     OUT = [Port() for _ in range(8)]
        ...     CLK = Port()
        ...     RST = Port()
        ...     VCC = Port()
        ...     GND = Port()
        ...
        ...     def __init__(self):
        ...         self.symbol = BoxSymbol(
        ...             rows=Row(
        ...                 left=PinGroup(self.IN),
        ...                 right=PinGroup(self.OUT)
        ...             ),
        ...             columns=Column(
        ...                 up=PinGroup([self.CLK, self.RST, self.VCC]),
        ...                 down=PinGroup(self.GND)
        ...             )
        ...         )

        >>> # Multiple rows for complex layouts
        >>> symbol = BoxSymbol(
        ...     rows=[
        ...         Row(left=PinGroup(data_pins), right=PinGroup(status_pins)),
        ...         Row(left=PinGroup(addr_pins), right=PinGroup(control_pins))
        ...     ],
        ...     columns=Column(up=PinGroup(power_pins), down=PinGroup(gnd_pins)),
        ...     config=BoxConfig(pin_spacing=1.0)
        ... )
    """

    config: BoxConfig
    width: float
    height: float
    symbol: SymbolBox
    mapping: SymbolMapping
    _rows: tuple[Row, ...]
    _columns: tuple[Column, ...]
    _left_row_spaces: tuple[SpaceEntry, ...]
    _right_row_spaces: tuple[SpaceEntry, ...]
    _up_col_spaces: tuple[SpaceEntry, ...]
    _down_col_spaces: tuple[SpaceEntry, ...]
    _x_offset: float
    _y_offset: float

    def __init__(
        self,
        rows: Row | Sequence[Row] = (),
        columns: Column | Sequence[Column] = (),
        config: BoxConfig | None = None,
        debug: bool = False,
        **kwargs,
    ):
        """
        Create a box symbol with the new row/column API

        Args:
            rows: Row object or sequence of Row objects defining the grid rows
            columns: Column object or sequence of Column objects defining the grid columns
            config: Box configuration object (optional)
            **kwargs: Additional configuration parameters that override the config object
        """
        from .context import SymbolStyleContext

        context = SymbolStyleContext.get()

        if config is None:
            if context is None:
                config = BoxConfig()
            else:
                config = context.box_config

        config = replace(config, **kwargs)

        # Create box configuration
        self.config = config

        # Convert single Row/Column objects to sequences
        if isinstance(rows, Row):
            rows = (rows,)
        if isinstance(columns, Column):
            columns = (columns,)

        # Auto-generate from component context if no rows/columns provided
        if not rows and not columns:
            try:
                rows, columns = self._auto_generate_from_component()
            except ValueError:
                # No component context available, keep empty rows/columns
                pass
        self._rows = tuple(rows or [Row()])
        self._columns = tuple(columns or [Column()])

        # Precalculate row and column spaces early for use in dimension calculation
        self._calculate_row_and_column_spaces()

        # Calculate box dimensions based on pin requirements to set width and height
        self._calculate_box_dimensions()

        # Initialize the symbol box
        self.symbol = SymbolBox(config)

        # Create the box shape, then adjust it to be on grid points when width and height are odd
        self._build_box_shape()

        # Build pins and symbol mapping
        self._build_pins()

        # Build labels
        self.symbol._build_labels(ref=Direction.Up, value=Direction.Down, margin=1)

        # Debug grid
        if debug:
            self._debug_grid()

    def _calculate_box_dimensions(self) -> None:
        """
        Calculate box dimensions based on precalculated row and column spaces.
        Sets 'width' and 'height' attributes.
        """
        # Use precalculated spaces to determine required dimensions
        # Width is determined by the largest column space (Up/Down directions)
        # Height is determined by the largest row space (Left/Right directions)

        # Set dimensions based on precalculated spaces
        required_width = sum(space.value for space in self._up_col_spaces)
        required_height = sum(space.value for space in self._left_row_spaces)

        self.width = max(self.config.min_width, required_width)
        self.height = max(self.config.min_height, required_height)

    def _build_box_shape(self) -> None:
        """
        Calculate the box shape based on the precalculated box width and height.
        Sets 'box', '_x_offset', and '_y_offset' attributes.
        """
        self.symbol.box = rectangle(self.width, self.height)
        # Track offset for grid lines
        self._x_offset = 0.0
        self._y_offset = 0.0
        if self.width % 2 != 0:
            self._x_offset = 0.5
            self.symbol.box = Transform((self._x_offset, 0.0)) * self.symbol.box
        if self.height % 2 != 0:
            self._y_offset = 0.5
            self.symbol.box = Transform((0.0, self._y_offset)) * self.symbol.box

    def _build_pins(self) -> None:
        """
        Calculate pin positions based on box dimensions and row/column layout,
        and add pins to the symbol.
        """

        def advance_space(
            current_pos: float, space_idx: int, spaces: Sequence[SpaceEntry]
        ) -> tuple[float, int]:
            """Helper to advance position and space index."""
            return current_pos + spaces[space_idx].value, space_idx + 1

        pin_positions = {}
        mappings = {}
        pins = []
        pin_decorators: Sequence[tuple[Shape, ...]] = []

        # Define direction configurations
        direction_configs = (
            (
                Direction.Left,
                [row.left for row in self._rows],
                self._left_row_spaces,
            ),
            (
                Direction.Right,
                [row.right for row in self._rows],
                self._right_row_spaces,
            ),
            (Direction.Up, [col.up for col in self._columns], self._up_col_spaces),
            (
                Direction.Down,
                [col.down for col in self._columns],
                self._down_col_spaces,
            ),
        )

        # Process each direction
        for direction, many_pin_groups, spaces in direction_configs:
            positions = []

            # Simply iterate through all spaces and calculate cumulative positions
            current_position = 0.0
            space_idx = 0

            def position_point(value: float, dir=direction) -> tuple[float, float]:
                if dir == Direction.Left:
                    pt = (-self.width / 2, self.height / 2 - value)
                elif dir == Direction.Right:
                    pt = (self.width / 2, self.height / 2 - value)
                elif dir == Direction.Up:
                    pt = (value - self.width / 2, self.height / 2)
                else:
                    pt = (value - self.width / 2, -self.height / 2)
                return math.ceil(pt[0]), math.ceil(pt[1])

            for pin_groups in many_pin_groups:
                # Skip spaces until we get to the content for this container
                while space_idx < len(spaces) and spaces[space_idx].type in (
                    SpaceType.CORNER,
                    SpaceType.ROW_COL_SPACING,
                    SpaceType.ROW_COL_SPACING_ALIGN,
                ):
                    current_position, space_idx = advance_space(
                        current_position, space_idx, spaces
                    )

                # Process pin groups for this container
                for group in pin_groups:
                    # Skip GROUP_SPACING before this group
                    if (
                        space_idx < len(spaces)
                        and spaces[space_idx].type == SpaceType.GROUP_SPACING
                    ):
                        current_position, space_idx = advance_space(
                            current_position, space_idx, spaces
                        )

                    # Skip PRE_PIN_SPACING before this group
                    if (
                        space_idx < len(spaces)
                        and spaces[space_idx].type == SpaceType.PRE_PIN_SPACING
                    ):
                        current_position, space_idx = advance_space(
                            current_position, space_idx, spaces
                        )

                    # Position pins in this group
                    for pin in group.pins:
                        at = position_point(current_position)
                        positions.append((pin, at))

                        if decorator := PinDecorator.get(pin):
                            pin_decorators.append(draw(decorator.spec, direction, at))

                        # Advance space to next pin position (if not at the last pin in this group)
                        go_next = False
                        while not go_next:
                            current_position, space_idx = advance_space(
                                current_position, space_idx, spaces
                            )
                            if space_idx >= len(spaces):
                                go_next = True
                            elif spaces[space_idx].type != SpaceType.PRE_PIN_SPACING:
                                go_next = True
            pin_positions[direction] = positions

        # Create pins for each direction (in order)
        for direction in [
            Direction.Up,
            Direction.Right,
            Direction.Down,
            Direction.Left,
        ]:
            for port, pos in pin_positions[direction]:
                # Create pin with appropriate settings based on decorator placement
                decorator = PinDecorator.get(port)
                pin_name_size = (
                    0
                    if (
                        decorator
                        and placement(decorator.spec) == DecoratorPlacement.INSIDE
                    )
                    else None
                )

                pin = Pin(
                    at=pos,
                    direction=direction,
                    length=self.config.pin_length,
                    pin_name_size=pin_name_size,
                )

                mappings[port] = pin
                pins.append(pin)

        self.symbol.set_pins(pins)
        self.symbol.decorators = tuple(pin_decorators)
        self.mapping = SymbolMapping(mappings)

    def _debug_grid(self):
        debug_grid = []
        line_width = 0.05
        thick_width = line_width * 4
        diagonal_width = line_width * 0.5
        margin = self.config.pin_length + 1

        # Box boundaries
        x0, x1 = -self.width / 2 + self._x_offset, self.width / 2 + self._x_offset
        y0, y1 = -self.height / 2 + self._y_offset, self.height / 2 + self._y_offset

        content_spaces = (
            SpaceType.PIN_SPACING,
            SpaceType.PRE_PIN_SPACING,
            SpaceType.GROUP_SPACING,
            SpaceType.ROW_COL_SPACING_ALIGN,
        )

        def add_grid_lines(spaces: Sequence[SpaceEntry], is_horizontal=True):
            """Add grid lines for either rows (horizontal) or columns (vertical)."""
            space_tally = 0
            prev_tally = 0
            diagonal_spacing = 0.4

            space_index = 0
            while space_index < len(spaces):
                space = spaces[space_index]
                space_tally += space.value

                if space.type in content_spaces:
                    if is_horizontal:
                        y = y1 - prev_tally
                        debug_grid.append(
                            Polyline(line_width, [(x0 - margin, y), (x1 + margin, y)])
                        )
                    else:
                        x = x0 + prev_tally
                        debug_grid.append(
                            Polyline(line_width, [(x, y0 - margin), (x, y1 + margin)])
                        )

                    # Content areas (PIN_SPACING and GROUP_SPACING) - thick lines + diagonal fill
                    while space.type in content_spaces:
                        if (
                            space_index < len(spaces) - 1
                            and spaces[space_index + 1].type in content_spaces
                        ):
                            space_tally += spaces[space_index + 1].value
                            space_index += 1
                        else:
                            break

                    if is_horizontal:
                        y_bottom, y_top = y1 - space_tally, y1 - prev_tally
                        # Thick border lines
                        for x in [x0 - margin, x1 + margin]:
                            debug_grid.append(
                                Polyline(thick_width, [(x, y_top), (x, y_bottom)])
                            )

                        # 45-degree diagonal fill (bottom-left to top-right for rows)
                        width = (x1 + margin) - (x0 - margin)
                        height = y_top - y_bottom

                        # Draw diagonals from bottom edge
                        x_pos = x0 - margin
                        while x_pos < x1 + margin:
                            # Calculate how far this diagonal can go
                            max_length = min((x1 + margin) - x_pos, height)
                            debug_grid.append(
                                Polyline(
                                    diagonal_width,
                                    [
                                        (x_pos, y_bottom),
                                        (x_pos + max_length, y_bottom + max_length),
                                    ],
                                )
                            )
                            x_pos += diagonal_spacing

                        # Draw diagonals from left edge to fill gaps
                        # Start from just above the bottom edge
                        y_pos = y_bottom + diagonal_spacing
                        while y_pos < y_top:
                            # Calculate how far this diagonal can go
                            max_length = min(width, y_top - y_pos)
                            debug_grid.append(
                                Polyline(
                                    diagonal_width,
                                    [
                                        (x0 - margin, y_pos),
                                        (x0 - margin + max_length, y_pos + max_length),
                                    ],
                                )
                            )
                            y_pos += diagonal_spacing

                    else:
                        x_start, x_end = x0 + prev_tally, x0 + space_tally
                        # Thick border lines
                        for y in [y0 - margin, y1 + margin]:
                            debug_grid.append(
                                Polyline(thick_width, [(x_start, y), (x_end, y)])
                            )

                        # 45-degree diagonal fill (top-left to bottom-right for columns)
                        width = x_end - x_start
                        height = (y1 + margin) - (y0 - margin)

                        # Draw diagonals from top edge
                        x_pos = x_start
                        while x_pos < x_end:
                            # Calculate how far this diagonal can go
                            max_length = min(x_end - x_pos, height)
                            debug_grid.append(
                                Polyline(
                                    diagonal_width,
                                    [
                                        (x_pos, y1 + margin),
                                        (x_pos + max_length, y1 + margin - max_length),
                                    ],
                                )
                            )
                            x_pos += diagonal_spacing

                        # Draw diagonals from left edge to fill gaps
                        y_pos = y1 + margin - diagonal_spacing
                        while y_pos > y0 - margin:
                            # Calculate how far this diagonal can go
                            max_length = min(width, y_pos - (y0 - margin))
                            debug_grid.append(
                                Polyline(
                                    diagonal_width,
                                    [
                                        (x_start, y_pos),
                                        (x_start + max_length, y_pos - max_length),
                                    ],
                                )
                            )
                            y_pos -= diagonal_spacing

                    if is_horizontal:
                        y = y1 - space_tally
                        debug_grid.append(
                            Polyline(line_width, [(x0 - margin, y), (x1 + margin, y)])
                        )
                    else:
                        x = x0 + space_tally
                        debug_grid.append(
                            Polyline(line_width, [(x, y0 - margin), (x, y1 + margin)])
                        )

                prev_tally = space_tally
                space_index += 1

        add_grid_lines(self._left_row_spaces, is_horizontal=True)
        add_grid_lines(self._up_col_spaces, is_horizontal=False)

        self.symbol._debug_grid = tuple(debug_grid)

    def _calculate_row_and_column_spaces(self) -> None:
        """Precalculate the space allocated for each row (Left/Right directions) and column (Up/Down directions).

        Each row must be wide enough to accommodate the widest slot from both
        Left and Right directions for that row index.
        Each column must be wide enough to accommodate the widest slot from both
        Up and Down directions for that column index.

        Sets '_row_spaces' and '_col_spaces' attributes.
        """

        # Calculate space needed for groups - returns sequence of SpaceEntry objects
        def pin_groups_space(pin_groups: Sequence[PinGroup]) -> Sequence[SpaceEntry]:
            if not pin_groups:
                return []

            spaces = []

            # Add pre margin for first group
            first_group = pin_groups[0]
            if first_group.pre_margin is not None:
                spaces.append(
                    SpaceEntry(first_group.pre_margin, SpaceType.GROUP_SPACING)
                )

            # Process each group
            for group_idx, group in enumerate(pin_groups):
                # Calculate pin spacing within the group, considering decorators
                # Create individual PIN_SPACING entries for each pin gap
                for pin_idx, pin in enumerate(group.pins):
                    # Calculate required spacing based on decorators
                    pin_space = self.config.pin_spacing

                    # Check current pin's decorator
                    pre_pin_space = False
                    decorator = PinDecorator.get(pin)
                    if decorator:
                        decorator_shapes = decorator.shapes()
                        bounds = reduce(
                            lambda a, b: a.union(b),
                            [s.to_shapely() for s in decorator_shapes],
                        ).bounds
                        decorator_size = bounds[3] - bounds[1]
                        if len(group.pins) == 1 and decorator_size <= pin_space:
                            pin_space = 0
                        elif pin_space < decorator_size:
                            pin_space = decorator_size / 2
                            pre_pin_space = True

                    # Create a PIN_SPACING entry for this specific pin gap
                    if pre_pin_space:
                        spaces.append(
                            SpaceEntry(math.ceil(pin_space), SpaceType.PRE_PIN_SPACING)
                        )
                    spaces.append(
                        SpaceEntry(
                            0
                            if (pin_idx == len(group.pins) - 1 and not pre_pin_space)
                            else math.ceil(pin_space),
                            SpaceType.PIN_SPACING,
                        )
                    )

                # Add spacing between groups (except for last group)
                if group_idx < len(pin_groups) - 1:
                    current_group = pin_groups[group_idx]
                    next_group = pin_groups[group_idx + 1]

                    post_margin = (
                        current_group.post_margin
                        if current_group.post_margin is not None
                        else 0
                    )
                    pre_margin = (
                        next_group.pre_margin
                        if next_group.pre_margin is not None
                        else 0
                    )

                    # If neither is defined, use group_spacing
                    if (
                        current_group.post_margin is None
                        and next_group.pre_margin is None
                    ):
                        spaces.append(
                            SpaceEntry(
                                self.config.group_spacing, SpaceType.GROUP_SPACING
                            )
                        )
                    else:
                        # Otherwise use the sum of the two margins
                        spaces.append(
                            SpaceEntry(
                                post_margin + pre_margin, SpaceType.GROUP_SPACING
                            )
                        )

            # Add post margin for last group
            last_group = pin_groups[-1]
            if last_group.post_margin is not None:
                spaces.append(
                    SpaceEntry(last_group.post_margin, SpaceType.GROUP_SPACING)
                )

            return spaces

        # Values alternate between margin and group, always starting and ending with a margin.
        left_row_spaces: Sequence[SpaceEntry] = []
        right_row_spaces: Sequence[SpaceEntry] = []
        up_col_spaces: Sequence[SpaceEntry] = []
        down_col_spaces: Sequence[SpaceEntry] = []
        corner_margin = self.config.corner_margin

        # Account for port names when managing corner margins to avoid overlap.
        ports = self._component_ports()
        ports_dict = dict(ports)

        def pair_ports_with_names(all_groups_in_dir: Sequence[Sequence[PinGroup]]):
            """Pair ports in the given pin groups with their path strings."""
            result = []
            for groups in all_groups_in_dir:
                for group in groups:
                    for port in group.pins:
                        if port in ports_dict:
                            result.append((port, ports_dict[port]))
            return result

        left_ports = pair_ports_with_names([row.left for row in self._rows])
        right_ports = pair_ports_with_names([row.right for row in self._rows])
        up_ports = pair_ports_with_names([col.up for col in self._columns])
        down_ports = pair_ports_with_names([col.down for col in self._columns])

        def max_name_length(port_list):
            """Get the maximum name length from a list of (port, name) tuples."""
            return max((len(name) for _, name in port_list), default=0)

        longest_left_port_name = max_name_length(left_ports)
        longest_right_port_name = max_name_length(right_ports)
        longest_up_port_name = max_name_length(up_ports)
        longest_down_port_name = max_name_length(down_ports)

        coeff = 0.5 * max(self.config.pin_name_size or 0.5, 0.5)

        row_corner_margin = max(
            corner_margin,
            math.ceil(coeff * (longest_up_port_name + longest_down_port_name)),
        )
        col_corner_margin = max(
            corner_margin,
            math.ceil(coeff * (longest_left_port_name + longest_right_port_name)),
        )

        if self._rows:
            corner = SpaceEntry(row_corner_margin, SpaceType.CORNER)
            left_row_spaces.append(corner)
            right_row_spaces.append(corner)

            # Add top margin for first row
            if self._rows[0].top_margin is not None:
                top_margin = SpaceEntry(
                    self._rows[0].top_margin, SpaceType.ROW_COL_SPACING
                )
                left_row_spaces.append(top_margin)
                right_row_spaces.append(top_margin)

            # Iterate pairwise through rows
            for i in range(len(self._rows)):
                current_row = self._rows[i]

                # Pin group spacing calculations
                left_spaces = pin_groups_space(current_row.left)
                right_spaces = pin_groups_space(current_row.right)
                left_row_spaces.extend(left_spaces)
                right_row_spaces.extend(right_spaces)
                left_space = sum(space.value for space in left_spaces)
                right_space = sum(space.value for space in right_spaces)

                if left_space < right_space:
                    left_row_spaces.append(
                        SpaceEntry(
                            right_space - left_space, SpaceType.ROW_COL_SPACING_ALIGN
                        )
                    )
                elif right_space < left_space:
                    right_row_spaces.append(
                        SpaceEntry(
                            left_space - right_space, SpaceType.ROW_COL_SPACING_ALIGN
                        )
                    )

                if i < len(self._rows) - 1:
                    next_row = self._rows[i + 1]

                    # Row margin calculations
                    top_margin = (
                        current_row.bottom_margin
                        if current_row.bottom_margin is not None
                        else 0
                    )
                    bottom_margin = (
                        next_row.top_margin if next_row.top_margin is not None else 0
                    )

                    # If neither row has margins defined, use row_spacing
                    if (
                        current_row.bottom_margin is None
                        and next_row.top_margin is None
                    ):
                        row_end = self.config.row_spacing
                    else:
                        # Otherwise use the sum of the two margins
                        row_end = bottom_margin + top_margin
                    row_end_entry = SpaceEntry(row_end, SpaceType.ROW_COL_SPACING)
                    left_row_spaces.append(row_end_entry)
                    right_row_spaces.append(row_end_entry)

            # Add bottom margin for last row
            last_row = self._rows[-1]
            if last_row.bottom_margin is not None:
                last_row_entry = SpaceEntry(
                    last_row.bottom_margin, SpaceType.ROW_COL_SPACING
                )
                left_row_spaces.append(last_row_entry)
                right_row_spaces.append(last_row_entry)
            left_row_spaces.append(corner)
            right_row_spaces.append(corner)

        if self._columns:
            corner = SpaceEntry(col_corner_margin, SpaceType.CORNER)
            up_col_spaces.append(corner)
            down_col_spaces.append(corner)

            # Add left margin for first column
            first_column = self._columns[0]
            if first_column.right_margin is not None:
                left_margin = SpaceEntry(
                    first_column.right_margin, SpaceType.ROW_COL_SPACING
                )
                up_col_spaces.append(left_margin)
                down_col_spaces.append(left_margin)

            # Iterate pairwise through columns
            for i in range(len(self._columns)):
                current_column = self._columns[i]

                # Pin group spacing calculations
                up_spaces = pin_groups_space(current_column.up)
                down_spaces = pin_groups_space(current_column.down)
                up_col_spaces.extend(up_spaces)
                down_col_spaces.extend(down_spaces)
                up_space = sum(space.value for space in up_spaces)
                down_space = sum(space.value for space in down_spaces)

                if up_space < down_space:
                    up_col_spaces.append(
                        SpaceEntry(
                            down_space - up_space, SpaceType.ROW_COL_SPACING_ALIGN
                        )
                    )
                elif down_space < up_space:
                    down_col_spaces.append(
                        SpaceEntry(
                            up_space - down_space, SpaceType.ROW_COL_SPACING_ALIGN
                        )
                    )

                if i < len(self._columns) - 1:
                    next_column = self._columns[i + 1]

                    # Column margin calculations
                    left_margin = (
                        current_column.right_margin
                        if current_column.right_margin is not None
                        else 0
                    )
                    right_margin = (
                        next_column.left_margin
                        if next_column.left_margin is not None
                        else 0
                    )

                    # If neither column has margins defined, use col_spacing
                    if (
                        current_column.right_margin is None
                        and next_column.left_margin is None
                    ):
                        col_end = self.config.col_spacing
                    else:
                        # Otherwise use the sum of the two margins
                        col_end = right_margin + left_margin
                    col_end_entry = SpaceEntry(col_end, SpaceType.ROW_COL_SPACING)
                    up_col_spaces.append(col_end_entry)
                    down_col_spaces.append(col_end_entry)

            # Add right margin for last column
            last_column = self._columns[-1]
            if last_column.right_margin is not None:
                last_column_entry = SpaceEntry(
                    last_column.right_margin, SpaceType.ROW_COL_SPACING
                )
                up_col_spaces.append(last_column_entry)
                down_col_spaces.append(last_column_entry)
            up_col_spaces.append(corner)
            down_col_spaces.append(corner)

        self._left_row_spaces = tuple(left_row_spaces)
        self._right_row_spaces = tuple(right_row_spaces)
        self._up_col_spaces = tuple(up_col_spaces)
        self._down_col_spaces = tuple(down_col_spaces)

    def _component_ports(self) -> Sequence[tuple[Port, str]]:
        """
        Get the ordered sequence of ports from the current component.
        """
        context = CurrentComponent.get()
        if context is None:
            raise ValueError("No component context available for auto-generation")
        component = context.component

        ports: Sequence[tuple[Port, str]] = []
        for trace, port in visit(component, Port):
            if port.is_single_pin():
                ports.append((port, pathstring(trace.path)))

        return ports

    def _auto_generate_from_component(self) -> tuple[Sequence[Row], Sequence[Column]]:
        """
        Auto-generate symbol layout from the current component context.

        Takes the ordered sequence of ports from the component and makes up to one cut
        to split them into Left and Right buckets while preserving their original order.
        Never cuts between ports with the same prefix.

        Returns:
            tuple of (rows, columns) for the symbol layout
        """
        ports = self._component_ports()

        # Extract prefixes to identify groups
        rgx = r"^([A-Za-z_]+(?:\[[^\]]*\])*?)(?:\.[A-Za-z_]+)*?(?=\[[^\]]*\]$|$)"
        prefixes = []
        for _, name in ports:
            match = re.match(rgx, name)
            prefix = match.group(1) if match else name
            prefixes.append(prefix)

        # Find valid cut points (where prefix changes)
        valid_cuts = []
        for i in range(1, len(prefixes)):
            if prefixes[i] != prefixes[i - 1]:
                valid_cuts.append(i)

        # Calculate desired cut points for even distribution
        total_ports = len(ports)
        desired_cut = total_ports // 2

        # Find nearest valid cuts
        def find_nearest_valid_cut(desired_cut: int) -> int:
            closest_cut = total_ports
            min_distance = float("inf")

            # Find the closest valid cut point
            for cut in valid_cuts:
                distance = abs(desired_cut - cut)
                if distance < min_distance:
                    min_distance = distance
                    closest_cut = cut

            return closest_cut

        cut = find_nearest_valid_cut(desired_cut)

        # Helper function to create PinGroups for each prefix section
        def create_pin_groups(ports: Sequence[tuple[Port, str]]) -> Sequence[PinGroup]:
            groups = []
            current_group = []
            current_prefix = None

            for port, name in ports:
                # Extract prefix from port name
                match = re.match(rgx, name)
                prefix = match.group(1) if match else name

                if current_prefix is None:
                    current_prefix = prefix
                    current_group = [port]
                elif prefix == current_prefix:
                    current_group.append(port)
                else:
                    # Prefix changed, create a group and start a new one
                    groups.append(PinGroup(current_group))
                    current_prefix = prefix
                    current_group = [port]

            # Don't forget the last group
            if current_group:
                groups.append(PinGroup(current_group))

            return groups

        # Create PinGroups for each direction
        left_groups = create_pin_groups(ports[:cut])
        right_groups = create_pin_groups(ports[cut:])

        # Create rows and columns
        rows = []
        columns = []

        # Left/Right go in rows
        if left_groups or right_groups:
            rows.append(Row(left=left_groups, right=right_groups))

        return rows, columns
