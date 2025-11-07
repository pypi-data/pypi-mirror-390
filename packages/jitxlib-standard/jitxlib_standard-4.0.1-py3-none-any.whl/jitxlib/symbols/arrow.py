"""
Arrow symbols module for JITX Standard Library

This module provides arrow symbol definitions and utilities for use
in various electrical symbols that require arrow indicators.
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from jitx.container import Composite
from jitx.shapes import Shape
from jitx.shapes.primitive import Polygon, Polyline
from jitx.transform import Transform

from .common import DEF_LINE_WIDTH


class ArrowStyle(Enum):
    """Arrow styles"""

    CLOSED_ARROW = "closed_arrow"
    OPEN_ARROW = "open_arrow"


# Arrow specific constants
DEF_ARROW_STYLE = ArrowStyle.OPEN_ARROW
DEF_HEAD_DIMS = (0.5, 0.5)
DEF_SHAFT_LEN = 1.0


@dataclass
class ArrowConfig:
    """Configuration for arrow symbols"""

    style: ArrowStyle = DEF_ARROW_STYLE
    head_dims: tuple[float, float] = DEF_HEAD_DIMS
    shaft_length: float = DEF_SHAFT_LEN
    line_width: float = DEF_LINE_WIDTH


@dataclass
class ArrowConfigurable:
    """Arrow configuration wrapper, useful for handling defaults"""

    arrow_config: ArrowConfig | None = None

    def __init__(self, arrow_config: ArrowConfig | None = None):
        self.arrow_config = arrow_config

    def get_arrow_config(self) -> ArrowConfig:
        """
        Returns the arrow configuration.

        If an arrow config is specified, it will be used.
        Otherwise, the config will be pulled from the context.
        If no context is available, a default config will be used.
        """
        from .context import SymbolStyleContext

        context = SymbolStyleContext.get()

        if self.arrow_config is None:
            if context is None:
                return ArrowConfig()
            else:
                return context.arrow_config
        else:
            return self.arrow_config


class Arrow(Composite):
    """Composite arrow shape with shaft and tip"""

    shaft: Shape[Polyline]
    tip: Shape[Polyline]

    def __init__(
        self,
        position: tuple[float, float],
        angle: float,
        config: ArrowConfig | None = None,
    ):
        """
        Create an arrow at a specific position and angle

        Args:
            position: (x, y) position for the arrow
            angle: Rotation angle in degrees
            config: ArrowConfig object, or None to use defaults
        """
        from .context import SymbolStyleContext

        context = SymbolStyleContext.get()

        if config is None:
            if context is None:
                config = ArrowConfig()
            else:
                config = context.arrow_config

        style, head_dims, shaft_length, line_width = (
            config.style,
            config.head_dims,
            config.shaft_length,
            config.line_width,
        )

        start = (line_width, 0.0)
        end = (shaft_length, 0.0)
        h, w = head_dims
        pts = [(w, h / 2.0), (0.0, 0.0), (w, h / -2.0)]

        if style == ArrowStyle.CLOSED_ARROW:
            tip = Polygon(pts)
        elif style == ArrowStyle.OPEN_ARROW:
            tip = Polyline(line_width, pts)
        else:
            raise ValueError(f"Invalid arrow style: {style}")

        shaft = Polyline(line_width, [start, end])

        self.shaft = Transform(position, angle) * shaft
        self.tip = Transform(position, angle) * tip
