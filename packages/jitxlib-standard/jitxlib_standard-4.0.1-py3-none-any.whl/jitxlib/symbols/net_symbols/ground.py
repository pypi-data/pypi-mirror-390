"""
Ground symbol for JITX Standard Library

This module defines the Ground symbol, often used as a net symbol, and associated construction functions.
"""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from jitx.compat.altium import AltiumSymbol, AltiumSymbolProperty
from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline
from jitx.symbol import Direction, Pin, SymbolOrientation

from ..common import DEF_LINE_WIDTH
from ..label import LabelConfigurable, LabelledSymbol

if TYPE_CHECKING:
    from ..context import SymbolStyleContext


# Ground symbol constants
DEF_GND_PORCH_WIDTH = 1.0
DEF_GND_SPACING = 0.4
DEF_GND_LINE_COUNT = 3
DEF_GND_MAX_LEN = 2.0
DEF_GND_MIN_LEN = 0.4


@dataclass
class GroundConfig(LabelConfigurable):
    """
    Configuration for ground symbols

    Defines the geometric and visual parameters for ground symbols.
    """

    line_width: float = DEF_LINE_WIDTH
    """Width of the ground symbol lines"""
    porch_width: float = DEF_GND_PORCH_WIDTH
    """Distance from pin to first horizontal line"""
    spacing: float = DEF_GND_SPACING
    """Vertical spacing between horizontal lines"""
    max_len: float = DEF_GND_MAX_LEN
    """Length of the longest line in the ground symbol"""
    min_len: float = DEF_GND_MIN_LEN
    """Length of the shortest line in the ground symbol"""
    line_count: int = DEF_GND_LINE_COUNT
    """Number of lines in the ground symbol"""

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.line_width <= 0:
            raise ValueError("Ground symbol line_width must be positive")
        if self.porch_width <= 0:
            raise ValueError("Ground symbol porch_width must be positive")
        if self.spacing <= 0:
            raise ValueError("Ground symbol spacing must be positive")
        if self.max_len <= 0:
            raise ValueError("Ground symbol max_len must be positive")
        if self.min_len <= 0:
            raise ValueError("Ground symbol min_len must be positive")
        if self.max_len < self.min_len:
            raise ValueError("Ground symbol max_len cannot be less than min_len")
        if self.line_count < 1:
            raise ValueError("Ground symbol must have at least one line")


class GroundSymbol(LabelledSymbol):
    """
    Ground symbol with graphics and pin.

    Creates a typical power ground net symbol consisting of horizontal lines
    of evenly decreasing length, evenly spaced in the -Y dimension.
    """

    config: GroundConfig
    vertical_line: Shape[Polyline]
    horizontal_lines: tuple[Shape[Polyline], ...]
    gnd: Pin

    def _lookup_config(
        self,
        config: GroundConfig | None = None,
        context: SymbolStyleContext | None = None,
    ) -> GroundConfig:
        """Lookup the config for this symbol."""
        if config is None:
            if context is None:
                return GroundConfig()
            return context.ground_config
        return config

    def __init__(self, config: GroundConfig | None = None, **kwargs):
        """
        Initialize ground symbol

        Args:
            config: GroundConfig, or None to use defaults
            **kwargs: Individual parameters to override defaults
        """
        # Apparently this needs to be imported here, even though SymbolStyleContext is imported in TYPE_CHECKING.
        from ..context import SymbolStyleContext

        context = SymbolStyleContext.get()
        config = self._lookup_config(config, context)
        self.config = replace(config, **kwargs)

        self._build_ground_symbol()
        self._build_pins()
        self._build_labels(value=Direction.Down)
        self.orientation = SymbolOrientation(0)
        AltiumSymbolProperty(AltiumSymbol.PowerGndPower).assign(self)

    def _build_pins(self) -> None:
        """Build 'gnd' symbol pin for the ground."""
        self.gnd = Pin(at=(0, 0), direction=Direction.Up)

    def _build_ground_symbol(self) -> None:
        """Build the ground symbol artwork."""
        # Vertical line from pin to first horizontal line
        self.vertical_line = Polyline(
            self.config.line_width,
            [(0.0, 0.0), (0.0, -self.config.porch_width)],
        )

        # Generate line lengths that decrease evenly from max_len to min_len
        line_lengths = self._generate_line_lengths()

        # Horizontal lines of decreasing length
        horizontal_lines = []
        for i, line_length in enumerate(line_lengths):
            half_width = line_length / 2.0
            y_pos = -self.config.porch_width - (i * self.config.spacing)

            line = Polyline(
                self.config.line_width,
                [(-half_width, y_pos), (half_width, y_pos)],
            )
            horizontal_lines.append(line)

        self.horizontal_lines = tuple(horizontal_lines)

    def _generate_line_lengths(self) -> tuple[float, ...]:
        """Generate evenly spaced line lengths from max_len to min_len."""
        if self.config.line_count == 1:
            return (self.config.max_len,)

        # Calculate the step size for even distribution
        step = (self.config.max_len - self.config.min_len) / (
            self.config.line_count - 1
        )

        # Generate lengths from max to min
        lengths = []
        for i in range(self.config.line_count):
            length = self.config.max_len - (i * step)
            lengths.append(length)

        return tuple(lengths)

    # Convenience properties to access config values
    @property
    def line_width(self) -> float:
        """See :attr:`~.GroundConfig.line_width`."""
        return self.config.line_width

    @property
    def porch_width(self) -> float:
        """See :attr:`~.GroundConfig.porch_width`."""
        return self.config.porch_width

    @property
    def spacing(self) -> float:
        """See :attr:`~.GroundConfig.spacing`."""
        return self.config.spacing

    @property
    def max_len(self) -> float:
        """See :attr:`~.GroundConfig.max_len`."""
        return self.config.max_len

    @property
    def min_len(self) -> float:
        """See :attr:`~.GroundConfig.min_len`."""
        return self.config.min_len

    @property
    def line_count(self) -> int:
        """See :attr:`~.GroundConfig.line_count`."""
        return self.config.line_count

    @property
    def line_lengths(self) -> tuple[float, ...]:
        """Generated line lengths from max_len to min_len."""
        return self._generate_line_lengths()

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config
